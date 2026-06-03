from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
import sqlite3, os, hashlib
from subs.apps_dashboard import (
    apps_monthly, apps_grid, apps_plant, apps_company,
    apps_quarterly, apps_histogram, apps_weekday, apps_donut
)

app = Flask(__name__)
app.secret_key = 'pcii_energia_2025_secret'

DB_PATH      = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'TrabalhoPCII.db')
DB_ACCESS_PW = 'pcii2026'   # senha de registo

# ── DB helpers ────────────────────────────────────────────────────────────────
def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    con = get_db()
    con.execute('''CREATE TABLE IF NOT EXISTS Users (
        user_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role     TEXT NOT NULL DEFAULT 'viewer'
    )''')
    con.commit(); con.close()

init_db()

# ── Auth decorators ────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def wrapped(*a, **kw):
        if 'username' not in session:
            flash('Faça login para continuar.', 'error')
            return redirect(url_for('login'))
        return f(*a, **kw)
    return wrapped

def admin_required(f):
    @wraps(f)
    def wrapped(*a, **kw):
        if session.get('role') != 'admin':
            flash('Sem permissão para esta ação.', 'error')
            return redirect(url_for('index'))
        return f(*a, **kw)
    return wrapped

# ── Auth routes ────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET','POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        con = get_db()
        user = con.execute('SELECT * FROM Users WHERE username=?', (username,)).fetchone()
        con.close()
        if user and user['password_hash'] == hash_pw(password):
            session['username'] = user['username']
            session['role']     = user['role']
            flash(f'Bem-vindo, {username}!', 'success')
            return redirect(url_for('index'))
        flash('Utilizador ou password incorretos.', 'error')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username  = request.form['username'].strip()
        password  = request.form['password']
        confirm   = request.form['confirm']
        role      = request.form['role']
        db_pass   = request.form['db_password']
        if db_pass != DB_ACCESS_PW:
            flash('Senha de acesso à base de dados incorreta.', 'error')
        elif not username:
            flash('Nome de utilizador é obrigatório.', 'error')
        elif len(password) < 4:
            flash('A password deve ter pelo menos 4 caracteres.', 'error')
        elif password != confirm:
            flash('As passwords não coincidem.', 'error')
        elif role not in ('admin', 'viewer'):
            flash('Papel inválido.', 'error')
        else:
            con = get_db()
            existing = con.execute('SELECT user_id FROM Users WHERE username=?', (username,)).fetchone()
            if existing:
                flash('Esse nome de utilizador já existe.', 'error')
                con.close()
            else:
                con.execute('INSERT INTO Users (username, password_hash, role) VALUES (?,?,?)',
                            (username, hash_pw(password), role))
                con.commit(); con.close()
                flash('Conta criada! Pode agora fazer login.', 'success')
                return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão terminada.', 'success')
    return redirect(url_for('login'))

# ── HOME ──────────────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def index():
    con = get_db()
    stats = {
        'companies':     con.execute('SELECT COUNT(*) FROM Company').fetchone()[0],
        'grids':         con.execute('SELECT COUNT(*) FROM Grid').fetchone()[0],
        'plants':        con.execute('SELECT COUNT(*) FROM Plant').fetchone()[0],
        'distributions': con.execute('SELECT COUNT(*) FROM Distribution').fetchone()[0],
    }
    con.close()
    return render_template('index.html', stats=stats)

@app.route('/api/dashboard')
@login_required
def api_dashboard():
    con = get_db()
    monthly = [dict(r) for r in con.execute("""
        SELECT strftime('%Y-%m', distribution_date) as month,
               ROUND(SUM(energy_supplied_kwh),2) as total,
               ROUND(AVG(energy_supplied_kwh),2) as avg,
               COUNT(*) as count
        FROM Distribution WHERE distribution_date IS NOT NULL
        GROUP BY month ORDER BY month
    """).fetchall()]
    per_grid = [dict(r) for r in con.execute("""
        SELECT g.grid_name as name, ROUND(SUM(d.energy_supplied_kwh),2) as total
        FROM Distribution d JOIN Grid g ON d.grid_id=g.grid_id
        GROUP BY g.grid_id ORDER BY total DESC LIMIT 10
    """).fetchall()]
    per_plant = [dict(r) for r in con.execute("""
        SELECT 'Central #'||p.plant_id as name, ROUND(SUM(d.energy_supplied_kwh),2) as total
        FROM Distribution d JOIN Plant p ON d.plant_id=p.plant_id
        GROUP BY p.plant_id ORDER BY total DESC LIMIT 10
    """).fetchall()]
    totals = con.execute("""
        SELECT ROUND(SUM(energy_supplied_kwh),2) as total,
               ROUND(AVG(energy_supplied_kwh),2) as avg,
               ROUND(MAX(energy_supplied_kwh),2) as max,
               COUNT(*) as count
        FROM Distribution
    """).fetchone()
    con.close()
    return jsonify({
        'monthly': monthly, 'per_grid': per_grid, 'per_plant': per_plant,
        'totals': {'total': totals['total'] or 0, 'avg': totals['avg'] or 0,
                   'max': totals['max'] or 0, 'count': totals['count'] or 0}
    })

# ── COMPANIES ─────────────────────────────────────────────────────────────────
@app.route('/companies')
@login_required
def companies():
    con = get_db()
    rows = con.execute('SELECT company_id, company_name, company_creation_date FROM Company ORDER BY company_id').fetchall()
    con.close()
    return render_template('companies/list.html', rows=rows)

@app.route('/companies/new', methods=['GET','POST'])
@login_required
@admin_required
def company_new():
    if request.method == 'POST':
        name = request.form['name'].strip()
        date = request.form['creation_date'].strip()
        if not name:
            flash('O nome da empresa é obrigatório.', 'error')
        else:
            con = get_db()
            max_id = con.execute('SELECT COALESCE(MAX(company_id),0) FROM Company').fetchone()[0]
            con.execute('INSERT INTO Company (company_id, company_name, company_creation_date) VALUES (?,?,?)', (int(max_id)+1, name, date))
            con.commit(); con.close()
            flash('Empresa criada!', 'success')
            return redirect(url_for('companies'))
    return render_template('companies/form.html', row=None)

@app.route('/companies/<int:cid>/edit', methods=['GET','POST'])
@login_required
@admin_required
def company_edit(cid):
    con = get_db()
    if request.method == 'POST':
        name = request.form['name'].strip()
        date = request.form['creation_date'].strip()
        if not name:
            flash('O nome da empresa é obrigatório.', 'error')
        else:
            con.execute('UPDATE Company SET company_name=?,company_creation_date=? WHERE company_id=?', (name,date,cid))
            con.commit(); con.close()
            flash('Empresa atualizada!', 'success')
            return redirect(url_for('companies'))
    row = con.execute('SELECT * FROM Company WHERE company_id=?', (cid,)).fetchone()
    con.close()
    return render_template('companies/form.html', row=row)

@app.route('/companies/<int:cid>/delete', methods=['POST'])
@login_required
@admin_required
def company_delete(cid):
    con = get_db()
    n = con.execute('SELECT COUNT(*) FROM Plant WHERE company_id=?', (cid,)).fetchone()[0]
    if n > 0:
        flash(f'Não é possível eliminar: {n} central(is) associada(s).', 'error')
    else:
        con.execute('DELETE FROM Company WHERE company_id=?', (cid,))
        con.commit(); flash('Empresa eliminada.', 'success')
    con.close()
    return redirect(url_for('companies'))

@app.route('/companies/bulk-delete', methods=['POST'])
@login_required
@admin_required
def company_bulk_delete():
    ids = request.form.getlist('ids')
    con = get_db(); deleted = errors = 0
    for cid in ids:
        n = con.execute('SELECT COUNT(*) FROM Plant WHERE company_id=?', (cid,)).fetchone()[0]
        if n > 0: errors += 1
        else:
            con.execute('DELETE FROM Company WHERE company_id=?', (cid,)); deleted += 1
    con.commit(); con.close()
    if deleted: flash(f'{deleted} empresa(s) eliminada(s).', 'success')
    if errors:  flash(f'{errors} empresa(s) ignorada(s) — têm centrais associadas.', 'error')
    return redirect(url_for('companies'))

# ── GRIDS ─────────────────────────────────────────────────────────────────────
@app.route('/grids')
@login_required
def grids():
    con = get_db()
    rows = con.execute('SELECT grid_id, grid_name, grid_address FROM Grid WHERE grid_id IS NOT NULL ORDER BY grid_id').fetchall()
    con.close()
    return render_template('grids/list.html', rows=rows)

@app.route('/grids/new', methods=['GET','POST'])
@login_required
@admin_required
def grid_new():
    if request.method == 'POST':
        name    = request.form['name'].strip()
        address = request.form['address'].strip()
        if not name:
            flash('O nome da rede é obrigatório.', 'error')
        else:
            con = get_db()
            max_id = con.execute('SELECT COALESCE(MAX(grid_id),0) FROM Grid').fetchone()[0]
            con.execute('INSERT INTO Grid (grid_id, grid_name, grid_address) VALUES (?,?,?)', (int(max_id)+1, name, address))
            con.commit(); con.close()
            flash('Rede criada!', 'success')
            return redirect(url_for('grids'))
    return render_template('grids/form.html', row=None)

@app.route('/grids/<int:gid>/edit', methods=['GET','POST'])
@login_required
@admin_required
def grid_edit(gid):
    con = get_db()
    if request.method == 'POST':
        name    = request.form['name'].strip()
        address = request.form['address'].strip()
        if not name:
            flash('O nome da rede é obrigatório.', 'error')
        else:
            con.execute('UPDATE Grid SET grid_name=?,grid_address=? WHERE grid_id=?', (name,address,gid))
            con.commit(); con.close()
            flash('Rede atualizada!', 'success')
            return redirect(url_for('grids'))
    row = con.execute('SELECT grid_id, grid_name, grid_address FROM Grid WHERE grid_id=?', (gid,)).fetchone()
    con.close()
    return render_template('grids/form.html', row=row)

@app.route('/grids/<int:gid>/delete', methods=['POST'])
@login_required
@admin_required
def grid_delete(gid):
    con = get_db()
    n = con.execute('SELECT COUNT(*) FROM Distribution WHERE grid_id=?', (gid,)).fetchone()[0]
    if n > 0:
        flash(f'Não é possível eliminar: {n} distribuição(ões) associada(s).', 'error')
    else:
        con.execute('DELETE FROM Grid WHERE grid_id=?', (gid,))
        con.commit(); flash('Rede eliminada.', 'success')
    con.close()
    return redirect(url_for('grids'))

@app.route('/grids/bulk-delete', methods=['POST'])
@login_required
@admin_required
def grid_bulk_delete():
    ids = request.form.getlist('ids')
    con = get_db(); deleted = errors = 0
    for gid in ids:
        n = con.execute('SELECT COUNT(*) FROM Distribution WHERE grid_id=?', (gid,)).fetchone()[0]
        if n > 0: errors += 1
        else:
            con.execute('DELETE FROM Grid WHERE grid_id=?', (gid,)); deleted += 1
    con.commit(); con.close()
    if deleted: flash(f'{deleted} rede(s) eliminada(s).', 'success')
    if errors:  flash(f'{errors} rede(s) ignorada(s) — têm distribuições associadas.', 'error')
    return redirect(url_for('grids'))

# ── PLANTS ────────────────────────────────────────────────────────────────────
@app.route('/plants')
@login_required
def plants():
    con = get_db()
    rows = con.execute("""
        SELECT p.plant_id, p.plant_comments, p.company_id, c.company_name
        FROM Plant p LEFT JOIN Company c ON p.company_id=c.company_id
        WHERE p.plant_id IS NOT NULL ORDER BY p.plant_id
    """).fetchall()
    con.close()
    return render_template('plants/list.html', rows=rows)

@app.route('/plants/new', methods=['GET','POST'])
@login_required
@admin_required
def plant_new():
    con = get_db()
    companies = con.execute('SELECT company_id,company_name FROM Company ORDER BY company_name').fetchall()
    if request.method == 'POST':
        company_id = request.form['company_id']
        comments   = request.form['comments'].strip()
        if not company_id:
            flash('A empresa proprietária é obrigatória.', 'error')
        else:
            max_id = con.execute('SELECT COALESCE(MAX(plant_id),0) FROM Plant').fetchone()[0]
            con.execute('INSERT INTO Plant (plant_id,company_id,plant_comments) VALUES (?,?,?)',
                        (int(max_id)+1, company_id, comments))
            con.commit(); con.close()
            flash('Central criada!', 'success')
            return redirect(url_for('plants'))
    con.close()
    return render_template('plants/form.html', row=None, companies=companies)

@app.route('/plants/<int:pid>/edit', methods=['GET','POST'])
@login_required
@admin_required
def plant_edit(pid):
    con = get_db()
    companies = con.execute('SELECT company_id,company_name FROM Company ORDER BY company_name').fetchall()
    if request.method == 'POST':
        company_id = request.form['company_id']
        comments   = request.form['comments'].strip()
        if not company_id:
            flash('A empresa proprietária é obrigatória.', 'error')
        else:
            con.execute('UPDATE Plant SET company_id=?,plant_comments=? WHERE plant_id=?', (company_id,comments,pid))
            con.commit(); con.close()
            flash('Central atualizada!', 'success')
            return redirect(url_for('plants'))
    row = con.execute('SELECT * FROM Plant WHERE plant_id=?', (pid,)).fetchone()
    con.close()
    return render_template('plants/form.html', row=row, companies=companies)

@app.route('/plants/<int:pid>/delete', methods=['POST'])
@login_required
@admin_required
def plant_delete(pid):
    con = get_db()
    n = con.execute('SELECT COUNT(*) FROM Distribution WHERE plant_id=?', (pid,)).fetchone()[0]
    if n > 0:
        flash(f'Não é possível eliminar: {n} distribuição(ões) associada(s).', 'error')
    else:
        con.execute('DELETE FROM Plant WHERE plant_id=?', (pid,))
        con.commit(); flash('Central eliminada.', 'success')
    con.close()
    return redirect(url_for('plants'))

@app.route('/plants/bulk-delete', methods=['POST'])
@login_required
@admin_required
def plant_bulk_delete():
    ids = request.form.getlist('ids')
    con = get_db(); deleted = errors = 0
    for pid in ids:
        n = con.execute('SELECT COUNT(*) FROM Distribution WHERE plant_id=?', (pid,)).fetchone()[0]
        if n > 0: errors += 1
        else:
            con.execute('DELETE FROM Plant WHERE plant_id=?', (pid,)); deleted += 1
    con.commit(); con.close()
    if deleted: flash(f'{deleted} central(is) eliminada(s).', 'success')
    if errors:  flash(f'{errors} central(is) ignorada(s) — têm distribuições associadas.', 'error')
    return redirect(url_for('plants'))

# ── DISTRIBUTIONS ─────────────────────────────────────────────────────────────
@app.route('/distributions')
@login_required
def distributions():
    con = get_db()
    rows = con.execute("""
        SELECT d.rowid, d.plant_id, d.grid_id, d.distribution_date, d.energy_supplied_kwh, g.grid_name
        FROM Distribution d
        LEFT JOIN Plant p ON d.plant_id=p.plant_id
        LEFT JOIN Grid  g ON d.grid_id =g.grid_id
        ORDER BY d.distribution_date DESC, d.plant_id
    """).fetchall()
    con.close()
    return render_template('distributions/list.html', rows=rows)

@app.route('/distributions/new', methods=['GET','POST'])
@login_required
@admin_required
def distribution_new():
    con = get_db()
    plants_list = con.execute('SELECT plant_id FROM Plant WHERE plant_id IS NOT NULL ORDER BY plant_id').fetchall()
    grids_list  = con.execute('SELECT grid_id, grid_name FROM Grid WHERE grid_id IS NOT NULL ORDER BY grid_name').fetchall()
    if request.method == 'POST':
        plant_id = request.form['plant_id']
        grid_id  = request.form['grid_id']
        date     = request.form['date'].strip()
        energy   = request.form['energy_kwh'].strip()
        if not all([plant_id, grid_id, date, energy]):
            flash('Todos os campos são obrigatórios.', 'error')
        else:
            con.execute('INSERT INTO Distribution (plant_id,grid_id,distribution_date,energy_supplied_kwh) VALUES (?,?,?,?)',
                        (plant_id, grid_id, date, float(energy)))
            con.commit(); con.close()
            flash('Distribuição registada!', 'success')
            return redirect(url_for('distributions'))
    con.close()
    return render_template('distributions/form.html', row=None, plants=plants_list, grids=grids_list)

@app.route('/distributions/<int:rowid>/edit', methods=['GET','POST'])
@login_required
@admin_required
def distribution_edit(rowid):
    con = get_db()
    plants_list = con.execute('SELECT plant_id FROM Plant WHERE plant_id IS NOT NULL ORDER BY plant_id').fetchall()
    grids_list  = con.execute('SELECT grid_id, grid_name FROM Grid WHERE grid_id IS NOT NULL ORDER BY grid_name').fetchall()
    if request.method == 'POST':
        plant_id = request.form['plant_id']
        grid_id  = request.form['grid_id']
        date     = request.form['date'].strip()
        energy   = request.form['energy_kwh'].strip()
        if not all([plant_id, grid_id, date, energy]):
            flash('Todos os campos são obrigatórios.', 'error')
        else:
            con.execute('UPDATE Distribution SET plant_id=?,grid_id=?,distribution_date=?,energy_supplied_kwh=? WHERE rowid=?',
                        (plant_id, grid_id, date, float(energy), rowid))
            con.commit(); con.close()
            flash('Distribuição atualizada!', 'success')
            return redirect(url_for('distributions'))
    row = con.execute('SELECT rowid,* FROM Distribution WHERE rowid=?', (rowid,)).fetchone()
    con.close()
    return render_template('distributions/form.html', row=row, plants=plants_list, grids=grids_list)

@app.route('/distributions/<int:rowid>/delete', methods=['POST'])
@login_required
@admin_required
def distribution_delete(rowid):
    con = get_db()
    con.execute('DELETE FROM Distribution WHERE rowid=?', (rowid,))
    con.commit(); con.close()
    flash('Distribuição eliminada.', 'success')
    return redirect(url_for('distributions'))

@app.route('/distributions/bulk-delete', methods=['POST'])
@login_required
@admin_required
def distribution_bulk_delete():
    ids = request.form.getlist('ids')
    con = get_db()
    for rid in ids:
        con.execute('DELETE FROM Distribution WHERE rowid=?', (rid,))
    con.commit(); con.close()
    flash(f'{len(ids)} distribuição(ões) eliminada(s).', 'success')
    return redirect(url_for('distributions'))


# ── DASHBOARD (Plotly) ────────────────────────────────────────────────────────
@app.route('/dashboard/monthly', methods=['GET','POST'])
@login_required
def dashboard_monthly():
    return apps_monthly()

@app.route('/dashboard/grid', methods=['GET','POST'])
@login_required
def dashboard_grid():
    return apps_grid()

@app.route('/dashboard/plant', methods=['GET','POST'])
@login_required
def dashboard_plant():
    return apps_plant()

@app.route('/dashboard/company', methods=['GET','POST'])
@login_required
def dashboard_company():
    return apps_company()

@app.route('/dashboard/quarterly', methods=['GET','POST'])
@login_required
def dashboard_quarterly():
    return apps_quarterly()

@app.route('/dashboard/histogram', methods=['GET','POST'])
@login_required
def dashboard_histogram():
    return apps_histogram()

@app.route('/dashboard/weekday', methods=['GET','POST'])
@login_required
def dashboard_weekday():
    return apps_weekday()

@app.route('/dashboard/donut', methods=['GET','POST'])
@login_required
def dashboard_donut():
    return apps_donut()

if __name__ == '__main__':
    app.run(debug=True)
