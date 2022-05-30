from turtle import width
from dash import Dash, dcc, html, Input, Output ,dash_table 
import dash
# import dash_core_components as dcc
# import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
# import dash_table
# import dash_bootstrap_components as dbc
import base64
# from dash import Dash, dcc, html, Input, Output
import plotly.express as px
# data = pd.read_csv("avocado.csv")
# data = data.query("type == 'conventional' and region == 'Albany'")
# data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d")
# data.sort_values("Date", inplace=True)
# df = pd.read_csv(r'MES.xlsx')
# z = [[.1, .3, .5, .7, .9]]

app = dash.Dash(__name__)

# Reference the underlying flask app (Used by gunicorn webserver in Heroku production deployment)
server = app.server 

df_MES = pd.read_csv(r'MES.csv')
df_MES.drop(['edwTxnTypeName','edwFromOperationName','edwToOperationName','edwFromStep_JobStep','edwToStep_JobStep','ReworkReasonName','edwReasonCodeName'],inplace=True,axis=1)
unique_drop_col = [column for column in df_MES.columns if df_MES[column].unique().shape[0] == 1]
df_MES.drop(unique_drop_col,axis=1,inplace=True)
df_MES['year'] = pd.to_datetime(df_MES['TxnDate']).apply(lambda x:x.year)
df_MES['day'] = pd.to_datetime(df_MES['TxnDate']).apply(lambda x:x.day)
df_MES['month'] = pd.to_datetime(df_MES['TxnDate']).apply(lambda x:x.month)
df_MES['weekday'] = pd.to_datetime(df_MES['TxnDate']).apply(lambda x:x.weekday())
df_MES['hour'] = pd.to_datetime(df_MES['TxnDate']).apply(lambda x:x.hour)
hour_dict = { '6':'6-7 AM','7':'7-8 AM','8':'8-9 AM','9':'9-10 AM','10':'10-11 AM','11':'11-12 AM','12':'12-1 PM','13':'1-2 PM','14':'2-3 PM','15':'3-4 PM','16':'4-5 PM','17':'5-6 PM','18':'6-7 PM','19':'7-8 PM','20':'8-9 PM','21':'9-10 PM','22':'10-11 PM','23':'11-12 PM'}
df_series = pd.Series(df_MES['hour'].value_counts().values,index=df_MES['hour'].value_counts().keys())
df_series.sort_index(inplace=True)
values = df_series.values * 100 / sum(df_series.values)
index = [*map(hour_dict.get,list(map(str,df_series.index)))]
anno_text = ['{:.1f}%'.format(i) for i in values]
values = values.reshape(18,1)
np.array(anno_text).reshape(18,1)
fig = ff.create_annotated_heatmap(values, y=index, annotation_text=np.array(anno_text).reshape(18,1),colorscale='ylgnbu')
fig['data'][0]['showscale'] = True
for i in range(len(fig.layout.annotations)):
    fig.layout.annotations[i].font.size = 8
# fig.update_layout(
#     yaxis = dict(
#         tickmode = 'array',
#         tickvals = [0],
#         ticktext = ['Transaction Count']
#     )
# )
annotation_text=[anno_text]
df_qty = df_MES.groupby(['edwEmployeeNumber'])['edwPreTxnContainerQty'].sum().reset_index()
df_qty['count'] = df_qty['edwEmployeeNumber'].map(df_MES['edwEmployeeNumber'].value_counts())
df_qty.set_index(['edwEmployeeNumber'],inplace=True)
df_rework = df_MES[df_MES['InRework'] == 'Y']
df_rework_qty = df_rework.groupby(['edwEmployeeNumber'])['edwPreTxnContainerQty'].sum().reset_index()
df_rework_qty['count'] = df_rework_qty['edwEmployeeNumber'].map(df_rework['edwEmployeeNumber'].value_counts())
df_rework_qty.set_index(['edwEmployeeNumber'],inplace=True)
pd.set_option('display.max_rows',None)
df_qty.columns = ['Pre Transaction Container qty', 'Pre Transaction Container Count']
df_rework_qty.columns = ['Rework Qty', 'Rework Transaction Count']
df_emp_final = pd.concat([df_qty,df_rework_qty],axis=1)
df_emp_final.fillna(0,inplace=True)
df_emp_final = df_emp_final.head(10)

# app.layout = html.Div([
   

#     dash_table.DataTable(
#         id='table_id',
#         columns = [{"name": i, "id": i,"selectable":False} for i in df_emp_final.columns],
#         data = df_emp_final.to_dict("rows"),
#         row_selectable="single",
#         fixed_rows={'headers': True, 'data': 0},
#         fixed_columns={'headers': True, 'data': 0},
#         style_header={
#             'backgroundColor': 'rgb(230, 230, 230)',
#             'fontWeight': 'bold'
#         },
#         style_table={
#             'maxWidth': '2000px',
#             'overflowX': 'scroll',
#             'border': 'thin lightgrey solid'
#         },
#         style_cell={
#         'font_family': 'cursive',
#         'font_size': '16px',
#         'border': '1px solid grey',
#         'minWidth': '1px', 'width': 'fixed', 'maxWidth': '1000px',
#         'textAlign': 'left', 'whiteSpace': 'normal'
#         }
#     ),

    
#     dcc.Graph(
#         id='life-exp-vs-gdp',
#         figure=fig
#     )
# ])
# import dash
# import dash_html_components as html
# import dash_core_components as dcc
app = dash.Dash()

# fig.show()
month_dict = {1:'Jan',12:'Dec'}
df_MES['day-month'] = df_MES['day'].astype(str) +"-"+ df_MES["month"].apply(lambda x: month_dict.get(x))
df_hour_day = df_MES.groupby(['hour','day-month']).size().reset_index(name='counts')
df_hour_day['counts'] = df_hour_day['counts'].apply(lambda x : x * 100 / len(df_MES))

df_hour_day.sort_values(by=['hour'],inplace=True)
result = df_hour_day.pivot(index='hour', columns='day-month', values='counts').reset_index()
result['hour'] = result['hour'].apply( lambda x : hour_dict.get(str(x)))
result.set_index(['hour'],inplace=True)
result.fillna(0,inplace=True)
fig2 = px.imshow(result.values,              
                labels=dict(x="Day of Week", y="Time of Day", color="Transaction Count Percentage"),
                x=result.columns,
                y=result.index,
                text_auto=True)
# fig2.update_layout(
#         margin=dict(l=20, r=20, t=20, b=20),
#         paper_bgcolor="LightSteelBlue")
# fig2.update_layout(width=1000)
fig2.update_layout(
    showlegend=False,
    width=100, height=500,
    autosize=True)
app.layout = html.Div(className="row",
        children=[
    html.Div(children=[
        dcc.Graph(id="graph2", figure=fig2,style={'display': 'inline-block'}),

    ])
])
# app.layout =  html.Div(className='row', children[
#         html.Div(
#             children=[
#         dcc.Graph(id="graph1", figure=fig,style={'width': '100','display': 'inline-block'}),
#         dcc.Graph(id="graph2", figure=fig,style={'wid th': '100','display': 'inline-block'})
#     ])
# ])

if __name__ == '__main__':
    app.run_server(debug=True)

# app = dash.Dash()

# image_filename = 'hourly line usage.png' # replace with your own image
# encoded_image = base64.b64encode(open(image_filename, 'rb').read())

# app.layout = html.Div([
#     html.Img(src=app.get_asset_url('hourly line usage.png'))
# ])
# if __name__ == "__main__":
#     app.run_server(debug=True)