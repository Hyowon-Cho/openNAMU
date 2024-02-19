from .tool.func import *

from .view_diff import view_diff_do

def edit_request(name = 'Test', do_type = ''):
    with get_db_connect() as conn:
        curs = conn.cursor()

        disable = ""
        if acl_check(name, 'document_edit') == 1:
            disabled = "disable"

        curs.execute(db_change("select id from history where title = ? order by id + 0 desc"), [name])
        doc_ver = curs.fetchall()
        doc_ver = doc_ver[0][0] if doc_ver else '0'

        curs.execute(db_change("select set_data from data_set where doc_name = ? and doc_rev = ? and set_name = 'edit_request_data'"), [name, doc_ver])
        db_data = curs.fetchall()
        if not db_data:
            return redirect('/edit/' + url_pas(name))
        
        edit_request_data = db_data[0][0]

        curs.execute(db_change("select set_data from data_set where doc_name = ? and doc_rev = ? and set_name = 'edit_request_user'"), [name, doc_ver])
        db_data = curs.fetchall()
        edit_request_user = db_data[0][0] if db_data else ''

        curs.execute(db_change("select set_data from data_set where doc_name = ? and doc_rev = ? and set_name = 'edit_request_date'"), [name, doc_ver])
        db_data = curs.fetchall()
        edit_request_date = db_data[0][0] if db_data else ''

        curs.execute(db_change("select set_data from data_set where doc_name = ? and doc_rev = ? and set_name = 'edit_request_send'"), [name, doc_ver])
        db_data = curs.fetchall()
        edit_request_send = db_data[0][0] if db_data else ''

        curs.execute(db_change("select set_data from data_set where doc_name = ? and doc_rev = ? and set_name = 'edit_request_leng'"), [name, doc_ver])
        db_data = curs.fetchall()
        edit_request_leng = db_data[0][0] if db_data else ''

        if flask.request.method == 'POST':
            if acl_check(name, 'document_edit') == 1:
                return redirect('/w/' + url_pas(name))
            
            curs.execute(db_change("select data from data where title = ?"), [name])
            db_data = curs.fetchall()
            o_data = db_data[0][0] if db_data else ''
            
            curs.execute(db_change("select user from scan where title = ? and type = ''"), [name])
            for scan_user in curs.fetchall():
                add_alarm(scan_user[0], edit_request_user, '<a href="/w/' + url_pas(name) + '">' + html.escape(name) + '</a>')

            if flask.request.form.get('check', '') == 'Y':
                curs.execute(db_change("delete from data where title = ?"), [name])
                curs.execute(db_change("insert into data (title, data) values (?, ?)"), [name, edit_request_data])
                        
                history_plus(
                    name,
                    edit_request_data,
                    edit_request_date,
                    edit_request_user,
                    edit_request_send,
                    edit_request_leng,
                    mode = 'edit_request'
                )
                
                render_set(
                    doc_name = name,
                    doc_data = edit_request_data,
                    data_type = 'backlink'
                )
            else:
                history_plus(
                    name,
                    o_data,
                    edit_request_date,
                    edit_request_user,
                    edit_request_send,
                    '0',
                    mode = 'edit_request'
                )
                
            if do_type == 'from':
                return redirect('/edit/' + url_pas(name))
            else:
                return redirect('/w/' + url_pas(name))
        else:
            curs.execute(db_change("select data from data where title = ?"), [name])
            db_data = curs.fetchall()
            old_data = db_data[0][0] if db_data else ''

            result = view_diff_do(old_data, edit_request_data, 'r' + doc_ver, load_lang('edit_request'))

            return easy_minify(flask.render_template(skin_check(), 
                imp = [name, wiki_set(), wiki_custom(), wiki_css(['(' + load_lang('edit_request_check') + ')', 0])],
                data = '''
                    <div id="opennamu_get_user_info">''' + html.escape(edit_request_user) + '''</div>
                    <hr class="main_hr">
                    ''' + edit_request_date + '''
                    <hr class="main_hr">
                    <input readonly value="''' + html.escape(edit_request_send) + '''">
                    <hr class="main_hr">
                    ''' + result + '''
                    <hr class="main_hr">
                    <form method="post">
                        <button id="opennamu_save_button" type="submit" name="check" value="Y">''' + load_lang('approve') + '''</button>
                        <button id="opennamu_preview_button" type="submit" name="check" value="">''' + load_lang('decline') + '''</button>
                        <hr class="main_hr">
                        <textarea readonly class="opennamu_textarea_500">''' + html.escape(edit_request_data) + '''</textarea>
                    </form>
                ''',
                menu = 0
            ))