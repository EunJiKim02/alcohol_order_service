# routes/main_routes.py
from flask import render_template, redirect, url_for, session, Blueprint, request, jsonify
from database.db import Oracledb
import json

main_bp = Blueprint('main', __name__)
oracle = Oracledb()

@main_bp.route('/')
def start():
    return render_template('main.html')

@main_bp.route('/aftersignin')
def aftersignin():
    return render_template('after_signin.html')

@main_bp.route('/random')
def random():
    if 'result_data' in session:
        result_data = session['result_data']
        session.pop('result_data', None)
    return render_template('random.html', data=result_data)

@main_bp.route('/index')
def main():
    if 'result_data' in session:
        result_data = session['result_data']
        session.pop('result_data', None)

        type_param = request.args.get('type', default='all', type=str)

        return render_template('index.html', data=result_data, status = type_param)
    
    elif 'userid' in session:
        type_param = request.args.get('type', default='all', type=str)
        if type_param == 'all':
            query = "SELECT A.Name, A.Price, A.Alcohol_degree, A.Type, round(avg(P.Star_rating),1) AS star, A.Alcohol_ID, A.Picture FROM ALCOHOL A, POINT P WHERE A.Alcohol_ID=P.Alcohol_ID group by A.Name, A.Price, A.Alcohol_degree, A.Type, A.Alcohol_ID, A.Picture order by DBMS_RANDOM.VALUE"
        elif type_param == 'etc':
            l = "('soju', 'beer', 'makgeolli', 'wine', 'sake', 'whiskey', 'tequila', 'brandy', 'gin', 'rum')"
            query = f"SELECT A.Name, A.Price, A.Alcohol_degree, A.Type, ROUND(AVG(P.Star_rating), 1) AS Avg_Star_Rating, A.Alcohol_ID,  A.Picture FROM ALCOHOL A JOIN POINT P ON A.Alcohol_ID = P.Alcohol_ID WHERE lower(A.Type) NOT IN {l} GROUP BY A.Name, A.Price, A.Alcohol_degree, A.Type, A.Alcohol_ID, A.Picture order by DBMS_RANDOM.VALUE"
        else:
            query = f"SELECT A.Name, A.Price, A.Alcohol_degree, A.Type, round(avg(P.Star_rating),1), A.Alcohol_ID,  A.Picture FROM ALCOHOL A, POINT P WHERE A.Alcohol_ID=P.Alcohol_ID and type like '%{type_param}%' group by A.Name, A.Price, A.Alcohol_degree, A.Type, A.Alcohol_ID, A.Picture order by DBMS_RANDOM.VALUE"
        result = oracle.selectall(query)

        return render_template('index.html', data=result, status = type_param)
    else:
        return redirect(url_for('auth.login'))
    

@main_bp.route('/search')
def search():
    return render_template('search.html')

@main_bp.route('/sample')
def sample():
    return render_template('sample.html')

@main_bp.route('/search_condition', methods=['GET'])
def search_condition():
    type = request.args.get('type')
    beer_type = request.args.get('beertype')
    beer_name = request.args.get('beername')
    minprice = request.args.get('minprice')
    maxprice = request.args.get('maxprice')
    star = request.args.get('starRating')

    condition = [beer_type, beer_name, minprice, maxprice, star]
   
    result = oracle.search(condition)
    if type == 'recommend':
        additioninfo = oracle.alcoholinfo(result[0][0])
        tmp = list(result[0])
        print("info: ", additioninfo)
        tmp.append(additioninfo[0])
        tmp.append(additioninfo[1])
        session['result_data'] = tmp

        return redirect(url_for('main.random'))
    elif type == 'search':
        session['result_data'] = result
        return redirect(url_for('main.main'))

@main_bp.route('/cover')
def cover():
    return render_template('cover.html')

@main_bp.route('/notice/<int:page_num>')
def notice(page_num):
    query = "SELECT * FROM NOTICE N order by written_date desc"
    result = oracle.selectall(query)
    page, result = oracle.selectpage(query, 20, page_num)
    return render_template('notice.html', page=page, data=result)

@main_bp.route('/find')
def find():
    return render_template('search.html')

@main_bp.route('/notice_contents/<noticeid>')
def notice_contents(noticeid):
    query = f"select writer, written_date, content from notice where notice_id = '{noticeid}'"
    res = oracle.select(query, 1)
    return render_template('notice_contents.html', data = res[0])

@main_bp.route('/store/<int:page_num>')
def store(page_num):
    query = "SELECT * FROM store"
    result = oracle.selectall(query)
    page, result = oracle.selectpage(query, 20, page_num)
    return render_template('store.html', page=page, data=result)


@main_bp.route('/detail/<alcohol_id>')
def detail(alcohol_id):
    print(alcohol_id)
    query = f"SELECT A.Name, A.Price, A.Alcohol_degree, A.Type, round(avg(P.Star_rating),1) AS star, A.Alcohol_ID, A.Picture FROM ALCOHOL A, POINT P WHERE A.Alcohol_ID=P.Alcohol_ID and A.Alcohol_ID = '{alcohol_id}' group by A.Name, A.Price, A.Alcohol_degree, A.Type, A.Alcohol_ID, A.Picture"
    
    result = oracle.select(query, 1)
    return render_template('uni_alcohol.html', data=result[0])