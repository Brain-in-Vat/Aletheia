import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from aletheia.settings import BASE_DIR
import json
import os
import statistics
import re

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
result_path = os.path.join(BASE_DIR, 'tmp', 'result2.json')

datas = []
with open(result_path, 'r') as f:
    # item = f.readline()
    for item in f.readlines():
        one_data = json.loads(item)
        datas.append(one_data)

total_df_dict = {
    'Gen': [],
    'Governance Loss': [],
    'data_type': []
}
for data in datas:
    gen = data['gen']
    best = data['best']['fitness']
    avg = [x['fitness'] for x in data['pop']]
    avg = statistics.mean(avg)
    total_df_dict['Gen'].append(gen)
    total_df_dict['Governance Loss'].append(avg)
    total_df_dict['data_type'].append('avg')

    total_df_dict['Gen'].append(gen)
    total_df_dict['Governance Loss'].append(best)
    total_df_dict['data_type'].append('best')

total_df = pd.DataFrame(data=total_df_dict)
total_fig = px.line(total_df, x='Gen', y='Governance Loss', color='data_type',
                    title='The Governance Loss Changing Along the Iteration')

best_data = datas[-1]['best']
best_data_loss_metric = best_data['measure']['loss_metric']

links = []
for data in datas:
    gen = data['gen']
    best = data['best']['fitness']
    avg = [x['fitness'] for x in data['pop']]
    avg = statistics.mean(avg)

    item = {
        'name': 'Gen {}'.format(gen),
        'href': '/gen_{}'.format(gen),
        'best': best,
        'avg': avg
    }
    links.append(item)

new_links = []
for link in links:
    new_links.append(html.Br())
    new_links.append(dcc.Link(link['name'], href=link['href']))

app.layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        dbc.Row(dbc.Col(html.H1(children='Algorithm Analyze',
                                style={'textAlign': 'center'}))),
        dbc.Row(dbc.Col(html.Div(children='''
            Analyze and visualize the result of Aletheia.
    ''', style={'textAlign': 'center'}))),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='example=graph',
                        figure=total_fig),
                ),

                dbc.Col(
                    html.Div(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H4("The Biggest Loss Situation",
                                                    className="card-title"),

                                            html.P(
                                                "Gonernance Loss : {}".format(
                                                    best_data['fitness']),
                                                className="card-text",
                                            ),

                                            html.P("Grant Loss : {}".format(
                                                best_data_loss_metric['token_loss']),
                                                className='card-text'),

                                            html.P("Token Loss : {}".format(
                                                best_data_loss_metric['grant_loss']),
                                                className='card-text'),

                                            dcc.Link(
                                                "details", "best-button", href="/best")
                                        ]
                                    ),
                                ],
                                style={"width": "30rem"},
                            )
                        ]
                    ),
                )
            ], align='center'),

        dbc.Row(dbc.Col(html.Div(id='page-content', children=new_links)))
    ]
)

index_page = html.Div(new_links)


def get_index_page(page, size=100):
    start = (page - 1) * size
    end = page * size
    tmp_links = links[start:end]
    card_links = []
    for link in tmp_links:
        card_content = [
            dbc.CardHeader(link['name']),
            dbc.CardBody([
                html.H5("Governance Loss", className="card-title"),

                html.P(
                    "Biggest Loss : {}".format(link['best']),
                    className="card-text",
                ),

                html.P(
                    "Avg Loss : {}".format(link['avg']),
                    className='card-text'
                ),

                dcc.Link('details', href=link['href'])
            ])
        ]
        card_links.append(card_content)

    link_number = len(tmp_links)
    result = []
    for i in range(1, 20):
        i_start = (i - 1) * 5
        i_end = i * 5
        if i_start >= link_number:
            break
        tmp_row = dbc.Row(
            [
                dbc.Col(x) for x in card_links[i_start: i_end]
            ]
        )
        result.append(tmp_row)

    next_page = page + 1
    result.append(dbc.Row([
        dbc.Col(
            [dcc.Link('Next Page', href='/top/page_{}'.format(next_page))], align='Right'
        )
    ]))

    page = html.Div(result)
    return page


def create_layout(gen, data, page, size=100):
    start = (page - 1) * size
    end = page * size
    pop = data['pop']
    pop = pop[start:end]
    tmp_links = []
    for index, item in enumerate(pop):
        tmp_links.append({
            'name': 'gen_{}_item_{}'.format(gen, index),
            'href': '/gen_{}/item_{}'.format(gen, index),
            'loss': item['fitness'],
            'grant_loss': item['measure']['loss_metric']['grant_loss'],
            'token_loss': item['measure']['loss_metric']['token_loss']
        })

    card_links = []
    for link in tmp_links:
        card_content = [
            dbc.CardHeader(link['name']),
            dbc.CardBody([
                html.H5('Governance Loss'),
                html.P('Loss : {}'.format(
                    link['loss']), className='card-text'),

                html.P('Grant Loss : {}'.format(
                    link['grant_loss']), className='card-text'),

                html.P('Token Loss : {}'.format(
                    link['token_loss']), className='card-text'),

                dcc.Link('details', href=link['href'])
            ])
        ]
        card_links.append(card_content)

        link_number = len(tmp_links)

        result = []
        for i in range(1, 20):
            i_start = (i - 1) * 5
            i_end = i * 5

            if i_start >= link_number:
                break
            tmp_row = dbc.Row(
                [
                    dbc.Col(x) for x in card_links[i_start: i_end]
                ]
            )
            result.append(tmp_row)

        # tmp_links.append(html.Br())
        # tmp_links.append(dcc.Link('gen_{}_item_{}'.format(
        #     gen, index), href='/gen_{}/item_{}'.format(gen, index)))

        next_page = page + 1
        result.append(dbc.Row([
            dbc.Col(
                [dcc.Link('Next Page', href='/gen_{}/page_{}'.format(gen, next_page))], align='Right'
            )
        ]))

    return html.Div(result)


def create_detail_fig(data):
    gene = data['Gene']
    agent_numer = int(len(gene) / 2)
    df_dict = {
        'belief': [x for x in gene[:agent_numer]],
        'tokens': [x for x in gene[agent_numer: agent_numer * 2]],
        'id': [x for x in range(agent_numer)]
    }

    data_df = pd.DataFrame(data=df_dict)
    # data_fig = px.scatter(data_df, x='belief', y='tokens')
    data_fig = px.scatter(data_df, x='id', y='belief',
                          size='tokens', size_max=60, title='Distribute of Belief and Tokens')

    clr_amount = {}
    data_results = data['measure']['results']
    for data_result in data_results:
        cls_grants = data_result['cls_grants']
        for cls_grant in cls_grants:
            index = cls_grant['id']

            if index in clr_amount:
                # clr_amount[cls_grant['id']] += cls_grant['clr_amount']
                clr_amount[index]['clr_amount'] += cls_grant['clr_amount']
                clr_amount[index]['number_contributions'] += cls_grant['number_contributions']
                clr_amount[index]['contribution_amount'] += cls_grant['contribution_amount']
            else:
                clr_amount[index] = {
                    'clr_amount': cls_grant['clr_amount'],
                    'number_contributions': cls_grant['number_contributions'],
                    'contribution_amount': cls_grant['contribution_amount']
                }

    clr_length = len(data_results)
    # clr_amount = {k: v/clr_length for k, v in clr_amount.items()}

    clr_amounts = [
        {
            'id': k,
            'clr_amount': v['clr_amount']/clr_length,
            'number_contributions': v['number_contributions'] / clr_length,
            'contribution_amount': v['contribution_amount'] / clr_length
        } for k, v in clr_amount.items()
    ]

    clr_df_dict = {
        'id': [],
        'clr_amount': [],
        'number_contributions': [],
        'contribution_amount': []
    }

    for clr_amount in clr_amounts:
        clr_df_dict['id'].append(clr_amount['id'])
        clr_df_dict['clr_amount'].append(clr_amount['clr_amount'])
        clr_df_dict['number_contributions'].append(
            clr_amount['number_contributions'])
        clr_df_dict['contribution_amount'].append(
            clr_amount['contribution_amount'])

    clr_df = pd.DataFrame(data=clr_df_dict)
    # clr_fig = px.bar(clr_df, x='id', y='clr_amount')
    clr_fig = px.bar(clr_df, x='id', y=[
                     'clr_amount', 'contribution_amount'], title='Distribution of Grant Amount and Contribution Amount')

    ctr_number_dict = {
        'id': [],
        'number_contributions': []
    }

    for clr_amount in clr_amounts:
        ctr_number_dict['id'].append(clr_amount['id'])
        ctr_number_dict['number_contributions'].append(
            clr_amount['number_contributions'])

    ctr_number_df = pd.DataFrame(data=ctr_number_dict)
    ctr_number_fig = px.bar(ctr_number_df, x='id', y='number_contributions',
                            title='Distribution of Contribution Number')

    token_changed = data['measure']['token_changed']
    token_changed_data = {
        'id': [],
        'value': []
    }
    for index, value in enumerate(token_changed):
        # token_changed_data[index] = value
        token_changed_data['id'].append(index)
        token_changed_data['value'].append(value)

    token_changed_df = pd.DataFrame(data=token_changed_data)
    token_changed_fig = px.scatter(
        token_changed_df, x='id', y='value', title='Dsitribution of Token Benefit')

    page_layout = html.Div([
        # html.H1('Agent Distribute'),
        dbc.Row(dbc.Col(html.H1('Agent Distribute'))),

        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='agents',
                        figure=data_fig,
                        style={'width': '100%'}
                    )
                ),

                dbc.Col(
                    dcc.Graph(
                        id='qf_amount',
                        figure=clr_fig,
                        style={'width': '100%'}
                    )
                ),

            ]
        ),

        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='token_changed',
                        figure=token_changed_fig,
                        style={'width': '100%'}
                    )
                ),

                dbc.Col(
                    dcc.Graph(
                        id='contribute_number',
                        figure=ctr_number_fig,
                        style={'width': '100%'}
                    )
                )

            ])
    ], style={'display': 'inline-block', 'width': '100%'})
    return page_layout


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    # if pathname in []:
    # if re.match(pathname, 'gen_\d')
    if re.match('^/gen_\d+$', pathname):
        gen_id = re.findall('\d+', pathname)
        gen_id = int(gen_id[0])
        data = datas[gen_id]
        return create_layout(gen_id, data, 1, 100)
    elif re.match('^/gen_\d+/item_\d+$', pathname):
        gen_ids = re.findall('\d+', pathname)
        gen_id = int(gen_ids[0])
        data_id = int(gen_ids[1])
        data = datas[gen_id]
        data = data['pop'][data_id]
        return create_detail_fig(data)
    elif pathname == '/best':
        return create_detail_fig(best_data)
    elif re.match('^/gen_\d+/page_\d+', pathname):
        gen_ids = re.findall('\d+', pathname)
        gen_id = int(gen_ids[0])
        page = int(gen_ids[1])
        data = datas[gen_id]
        return create_layout(gen_id, data, page, 100)
    elif re.match('^/top/page_\d+', pathname):
        gen_id = re.findall('\d+', pathname)
        page = int(gen_id[0])
        return get_index_page(page)
    else:
        return get_index_page(1)


if __name__ == '__main__':
    app.run_server(debug=False)
