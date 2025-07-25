from db import get_one_day_orders, get_money_balances, get_increment
from setting import BASE_DIR
from decimal import Decimal
from math import pow, ceil, log

import zmail
from datetime import datetime, timedelta


attachment_list = list()


def send(subject, content_html, attachments):
    username = 'zhufengkun@126.com'
    # 邮箱授权码
    authorization_code = 'FLJJQUDDZXBXBWQA'
    # 构建一个邮箱服务对象
    server = zmail.server(username, authorization_code)
    if attachments is None or len(attachments) == 0:
        mail_body = {
            'subject': subject,
            'content_html': content_html,  # 纯文本或者HTML内容
            'attachments': attachments,
        }
    else:
        mail_body = {
            'subject': subject,
            'content_html': content_html,  # 纯文本或者HTML内容
            'attachments': attachments,
        }
    mail_to = ['marc2719@163.com', 'zhufengxin@live.cn']
    server.send_mail(mail_to, mail_body)
    del server


def format_table_header(order):
    return "<td>{0}</td>".format('</td><td>'.join(order))


def format_table_body(bodys):
    html_body = str()
    for order in bodys:
        sub_body = ''
        for value in order.values():
            if isinstance(value, Decimal):
                sub_body += f'<td>{round(value, 6)}</td>'
            else:
                sub_body +=f'<td>{value}</td>'
        html_body += f'<tr>{sub_body}</tr>'
    return html_body


def gen_html(data_set):
    html = '''
<html>
    <body>
    <style type="text/css">
    table{
        width: 100%;
        border-collapse: separate;
        border-radius: 8px;
        border: 1px solid #000000;
    }

    table caption{
        font-size: 2em;
        font-weight: bold;
        margin: 1em 0;
    }

    th,td{
        border: 1px solid #999;
        text-align: center;
        padding: 20px 0;
    }

    table thead tr{
        background-color: #004646;
        color: #fff;
    }

    table tbody tr:nth-child(odd){
        background-color: #eee;
    }

    table tbody tr:hover{
        background-color: #ccc;
    }

    table tbody tr td:first-child{
        color: #f40;
    }

    table tfoot tr td{
        text-align: right;
        padding-right: 20px;
    }
    </style>
    <table cellspacing="0" border="1">
        <thead>
            <tr>
                {{html_header}}
            </tr>
        </thead>
        <tbody>
            {{html_body}}
        </tbody>
    </table>
    </body>
</html>'''

    if len(data_set) == 0:
        return html.replace('{{html_header}}', '<td>数量</td>').replace('{{html_body}}', '<tr><td>0</td></tr>')

    html_header = format_table_header(data_set[0].keys())
    html_body = str()
    html_body = format_table_body(bodys = data_set)

    html = html.replace('{{html_header}}', html_header)
    html = html.replace('{{html_body}}', html_body)
    return html


def save_html(html, name):
    report_path = f'{BASE_DIR}/report/{name}.html'
    with open(file=report_path, mode='w') as f:
        f.write(html)
    return report_path


def body():
    return """<h1>欧易日常报表:</h1>
        <p>今天的交易情况</p>
        <p>当前资金池</p>
    """

def gen_report(func, name):
    data_set = func()
    html = gen_html(data_set=data_set)
    report = save_html(html=html, name=name)
    return report

def increment():
    data_set = get_increment()
    new_data_set = list()
    for data in data_set:
        if data['incre'] is None or float(data['incre']) <= 0:
            continue

        new_data = dict()
        new_data['目标'] = float(ceil(data['incre']))
        new_data['instId'] =data['instId']
        new_data['开始日期'] = data['create_date']
        new_data['历史增长率'] = float(data['incre'])
        if new_data.get('历史增长率') == 1:
            continue
        new_data['历史订单数'] = int(data['orders'])
        if new_data['历史订单数'] == 0:
            continue
        if (datetime.today() - new_data['开始日期']).days == 0:
            continue
        new_data['金额拆分数'] = int(data['counts'])
        new_data['批量交易数'] = new_data['历史订单数'] / (new_data['金额拆分数'] * 2)
        new_data['平均增长率'] = pow(float(new_data['历史增长率']), (1 / new_data['批量交易数']))
        new_data['总体交易数'] = log(float(new_data['目标']), float(new_data['平均增长率']))
        new_data['剩余订单数'] = (new_data['金额拆分数'] * 2) * (new_data['总体交易数'] - new_data['批量交易数'])
        new_data['距离目标天数'] = ceil(new_data['剩余订单数'] / (new_data['历史订单数'] / (datetime.today() - new_data['开始日期']).days))
        new_data['距离目标日期'] = (datetime.today() + timedelta(days=new_data['距离目标天数'])).strftime('%Y%m%d')
        new_data_set.append(new_data)

    return new_data_set

def start():
    attchment_list = list()
    set_list = [
        {'name': 'daily_orders', 'func': get_one_day_orders},
        {'name': 'money_report', 'func': get_money_balances},
        {'name': 'increment', 'func': increment}
    ]
    
    for data in set_list:
        report = gen_report(name = data.get('name'),
            func = data.get('func')
        )
        attchment_list.append(report)

    send(
        subject=datetime.today().strftime("欧易日常数据：%Y-%m-%d"),
        content_html=body(),
        attachments=attchment_list
    )
