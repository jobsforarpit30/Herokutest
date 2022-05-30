import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
from dash import Dash, dcc, html, Input, Output ,dash_table 
import plotly.figure_factory as ff


app = Dash(__name__)

df_MES= pd.read_csv(r"MES.csv")
df_MES['year'] = pd.to_datetime(df_MES['TxnDate']).apply(lambda x: x.year)
df_MES['month'] = pd.to_datetime(df_MES['TxnDate']).apply(lambda x: x.month)
df_MES['hour'] = pd.to_datetime(df_MES['TxnDate']).apply(lambda x: x.hour)
df_MES['day'] = pd.to_datetime(df_MES['TxnDate']).apply(lambda x: x.day)
df_MES['hour'] = pd.to_datetime(df_MES['TxnDate']).apply(lambda x:x.hour)
hour_dict = { '6':'6-7 AM','7':'7-8 AM','8':'8-9 AM','9':'9-10 AM','10':'10-11 AM','11':'11-12 AM','12':'12-1 PM','13':'1-2 PM','14':'2-3 PM','15':'3-4 PM','16':'4-5 PM','17':'5-6 PM','18':'6-7 PM','19':'7-8 PM','20':'8-9 PM','21':'9-10 PM','22':'10-11 PM','23':'11-12 PM'}




app.layout =html.Div(children=[ html.Div([html.H1(children="Edward Pharmaceuticals Operations Dashboard",  style={'text-align': 'center'})]),
 html.Div([
    html.H2(children="Employee Performance Analysis",  style={'text-align': 'center'}),
    dcc.Dropdown(id="slct_year1",
                options=[
                    {"label": "2020", "value": 2020},
                    {"label": "2021", "value": 2021},
                    {"label": "All", "value": 'All'},
                    ],
                multi=False,
                value='All',
                style={'width': "40%"}
                ),
    dcc.Dropdown(id="slct_month1",
                    options=[
                        {"label": "January", "value": 1},
                        {"label": "December", "value": 12},
                        {"label": "All", "value": 'All'},
                        ],
                    multi=False,
                    value='All',
                    style={'width': "40%"}
                    ),
    #html.Div(id='output_container1', children=[]),
    html.Br(),

    dcc.Graph(id='fig2')

])])

@app.callback(
    [
        Output('fig2', 'figure')
    ],
    [Input("slct_year1", "value")],
    [Input("slct_month1", "value")] 
)
def update_graph(se_year,month):
    

    #containe = "The year chosen by user was: {}".format(year)
    df_emp=df_MES.groupby(['year','month','edwEmployeeNumber']).agg({'edwPreTxnContainerQty':'sum'}).reset_index()
    df_emp1=df_MES.groupby(['year','month','edwEmployeeNumber','InRework']).agg({'edwPreTxnContainerQty':'sum'}).reset_index()
   

    if (se_year == 'All') & (month == 'All'):
        # df_new=df_emp.nlargest(10,columns='edwPreTxnContainerQty')
        # df_new['edwEmployeeNumber']=df_new.edwEmployeeNumber.astype('str')
        
        # fig2 = px.bar(df_new, x='edwEmployeeNumber',y='edwPreTxnContainerQty', labels={'edwEmployeeNumber':'Employee Number','edwPreTxnContainerQty':'Production Qty'})
        
        ### heatmap fig3
        # df_series = pd.Series(df_MES['hour'].value_counts().values,index=df_MES['hour'].value_counts().keys())
        # df_series.sort_index(inplace=True)
        # values = df_series.values * 100 / sum(df_series.values)
        # index = [*map(hour_dict.get,list(map(str,df_series.index)))]
        # anno_text = ['{:.1f}%'.format(i) for i in values]
        # values = values.reshape(18,1)
        # np.array(anno_text).reshape(18,1)
        # fig3 = ff.create_annotated_heatmap(values, y=index, annotation_text=np.array(anno_text).reshape(18,1),colorscale='ylgnbu')
        # fig3['data'][0]['showscale'] = True
        # for i in range(len(fig3.layout.annotations)):
        #     fig3.layout.annotations[i].font.size = 8
        
        # #####Bar chart
        # values = df_series.values * 100 / sum(df_series.values)
        # df_peak_bar = pd.DataFrame({'hour':index,'values':values})
        # fig4 = px.bar(df_peak_bar, x='hour', y='values')
        # fig4 = fig2
        month_dict = {1:'Jan',12:'Dec'}
        df_MES['day-month'] = df_MES['day'].astype(str) +"-"+ df_MES["month"].apply(lambda x: month_dict.get(x))
        df_hour_day = df_MES.groupby(['hour','day-month']).size().reset_index(name='counts')
        df_hour_day['counts'] = df_hour_day['counts'].apply(lambda x : x * 100 / len(df_MES))

        df_hour_day.sort_values(by=['hour'],inplace=True)
        result = df_hour_day.pivot(index='hour', columns='day-month', values='counts').reset_index()
        result['hour'] = result['hour'].apply( lambda x : hour_dict.get(str(x)))
        result.set_index(['hour'],inplace=True)
        result.fillna(0,inplace=True)
        fig2 = px.imshow(result.values
                # labels=dict(x="Day of Week", y="Time of Day", color="Transaction Count Percentage"),
                # x=result.columns,
                # y=result.index,
                # text_auto=True
               )
        # fig2.update_xaxes(side="top")


        # for t in ax.texts: t.set_text(t.get_text() + " %")
   

        ### Rework chart
        # z=df_emp1[df_emp1['InRework']=='Y']
        # y=df_MES.groupby('edwEmployeeNumber',as_index=False)['edwPreTxnContainerQty'].agg('sum')
        # z.rename(columns={'edwPreTxnContainerQty':'ReworkQTY'},inplace=True)
        # z1=z[["edwEmployeeNumber","ReworkQTY"]]

        # m=y.merge(z1,how='left',on='edwEmployeeNumber').fillna(0)
        # final=m.sort_values('ReworkQTY',ascending=False).reset_index()
        # final['%ReworkQTY']=((final['ReworkQTY']/final['edwPreTxnContainerQty'])*100).round(2)
        # df_emp_final_new=final.head(14).sort_values('%ReworkQTY',ascending=False)
        # df_emp_final_new.drop('index',axis=1, inplace=True)
        # fig5 = px.bar(df_emp_final_new, x='edwEmployeeNumber',y=['edwPreTxnContainerQty','ReworkQTY'] )
        
        return fig2


    # Plotly Express
    else:
        dff = df_emp.copy()
        dff = dff[dff["year"] == se_year]
        dff = dff[dff["month"] == month]
        df_new=dff.nlargest(10,columns='edwPreTxnContainerQty')
        df_new['edwEmployeeNumber']=df_new.edwEmployeeNumber.astype('str')
        fig2 = px.bar(df_new, x='edwEmployeeNumber',y='edwPreTxnContainerQty', labels={'edwEmployeeNumber':'Employee Number','edwPreTxnContainerQty':'Production Qty'})
        
        ### heatmap
        # df_peak = df_MES[df_MES["year"] == se_year]
        # df_peak = df_peak[df_peak["month"] == month]
        # df_series = pd.Series(df_peak['hour'].value_counts().values,index=df_peak['hour'].value_counts().keys())
        # df_series.sort_index(inplace=True)
        # values = df_series.values * 100 / sum(df_series.values)
        # index = [*map(hour_dict.get,list(map(str,df_series.index)))]
        # anno_text = ['{:.1f}%'.format(i) for i in values]
        # values = values.reshape(18,1)
        # np.array(anno_text).reshape(18,1)
        # fig3 = ff.create_annotated_heatmap(values, y=index, annotation_text=np.array(anno_text).reshape(18,1),colorscale='ylgnbu')
        # fig3['data'][0]['showscale'] = True
        # for i in range(len(fig3.layout.annotations)):
        #     fig3.layout.annotations[i].font.size = 8        
        
        # #####Bar chart
        # values = df_series.values * 100 / sum(df_series.values)
        # df_peak_bar = pd.DataFrame({'hour':index,'values':values})
        # fig4 = px.bar(df_peak_bar, x='hour', y='values')

        # ### Rework chart
        # dff1 = df_emp1.copy()
        # dff1 = dff1[dff1["year"] == se_year]
        # dff1 = dff1[dff1["month"] == month]        
        # z=dff1[dff1['InRework']=='Y']
        # y=dff1.groupby('edwEmployeeNumber',as_index=False)['edwPreTxnContainerQty'].agg('sum')
        # z.rename(columns={'edwPreTxnContainerQty':'ReworkQTY'},inplace=True)
        # z1=z[["edwEmployeeNumber","ReworkQTY"]]

        # m=y.merge(z1,how='left',on='edwEmployeeNumber').fillna(0)
        # final=m.sort_values('ReworkQTY',ascending=False).reset_index()
        # final['%ReworkQTY']=((final['ReworkQTY']/final['edwPreTxnContainerQty'])*100).round(2)
        # df_emp_final_new=final.head(14).sort_values('%ReworkQTY',ascending=False)
        # df_emp_final_new.drop('index',axis=1, inplace=True)
        # fig5 = px.bar(df_emp_final_new, x='edwEmployeeNumber',y=['edwPreTxnContainerQty','ReworkQTY'])

        return fig2

       



if __name__== "__main__":
    app.run_server()