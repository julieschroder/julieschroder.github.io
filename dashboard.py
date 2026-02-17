

import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_holoniq_wordcloud import DashWordcloud
import plotly.express as px
import plotly.graph_objects as go


app = dash.Dash(__name__)
server = app.server

data1 = pd.read_csv('First_clean.csv') 
data2 = pd.read_csv('Second_clean.csv')

medal_colors = data2['medal_color'].unique().tolist()
medal_colors.append('All')

merged = data1.merge(data2,left_on="id",right_on="id")

n_medals = pd.DataFrame(data2[["id", "medal_color"]].value_counts().reset_index(name="number_medals"))
n_medals2 = n_medals.replace({'gold': '1', 'silver': '2', 'bronze': '3'}).rename(columns={"medal_color": "placement"})

# merged = data1.merge(data2,left_on="id",right_on="id")


app.layout = html.Div([
        html.H1("Danish Olympic Medalists", 
                style = {'textAlign':'center', 'font-family': 'Impact', 'font-size': '3rem'}),
        html.P("Select a medal color:", 
                style = {'textAlign':'center', 'font-family' : 'Helvetica', 'font-size': '1.5rem'}),        
        html.Div([
            dcc.Dropdown(
                id='medal_color',
                options=[{'label': i.capitalize(), 'value': i} for i in medal_colors],
                value='All'
            ),
            html.Button(id='resetAll', children = 'Remove all filters', n_clicks = 0)
        ], style={'width':'50%', 'margin':'0 auto'}),
        html.Div([
            html.Div([ 
                html.H2("Wordcloud of Sport", 
                        style = {'textAlign':'center', 'font-family' : 'Helvetica', 'font-size': '1.75rem'}),
                html.P("Select a sport in the wordcloud to see associated disciplines", 
                        style = {'textAlign':'center', 'font-family' : 'Helvetica', 'font-size': '1rem'}),
                html.Button(id='resetCloud', children = 'Remove sport filter', n_clicks = 0),
                html.Div([
                        html.Div([DashWordcloud( 
                            id='wordcloud',
                            list=[],
                            width=800, 
                            height=400,
                            gridSize=15,
                            color='random-dark',
                            backgroundColor='lightblue',
                            shuffle=False,
                            rotateRatio=0.5 ,
                            shrinkToFit=True,
                            hover=True) 
                            ],style={'margin':'0 auto'}),
                        
                        html.Div([dcc.Graph(id='discipline_table',
                                  config = {'displayModeBar': False})
                            ],style={'margin':'0 auto'})
                ])
            ],style={'width':'60%','display':'inline-block'}),
            html.Div([
                html.H2("Olympic Events", 
                        style = {'textAlign':'center', 'font-family' : 'Helvetica', 'font-size': '1.75rem'}),    
                html.P("Select an olympic event", 
                        style = {'textAlign':'center', 'font-family' : 'Helvetica', 'font-size': '1rem'}),
                html.Button(id='resetBar', children = 'Remove olympic event filter', n_clicks = 0),
                dcc.Graph(id='medal_chart',
                          config = {'displayModeBar': False})
                ],style={'width':'40%', 'display':'inline-block'}),
        ]),
        
        html.Div([            
            html.Div([
                html.H2("Medalists", 
                        style = {'textAlign':'center', 'font-family' : 'Helvetica', 'font-size': '1.75rem'}),
                html.P("Ordered by the number of gold, silver and bronze medals", 
                        style = {'textAlign':'center', 'font-family' : 'Helvetica', 'font-size': '1rem'}),
                dcc.Graph(id='medalist_table',
                          config = {'displayModeBar': False})
                ],style={'margin':'0 auto'})
        ])
],style={'background-color': 'lightblue'})


def filter_data(medal_color):
    
    mydata = merged
    if medal_color != 'All':
        mydata = merged[merged["medal_color"] == medal_color]
    
    return mydata

    
@app.callback(
    Output(component_id='medalist_table', component_property='figure'),
    [
        Input(component_id='medal_color', component_property='value'),
        Input(component_id='medal_chart', component_property='clickData'),
        Input(component_id='wordcloud', component_property='click'),
        
    ],
)

def update_table(medal_color, clickData, click_word):
    
    mydata = filter_data(medal_color)
    
    event = None
    if clickData != None:
        event = clickData["points"][0]["x"]
        mydata = mydata[mydata["year"] == event]
        
    sport = None
    if click_word != None: 
           sport = click_word[0] 
           mydata = mydata[mydata['sport'] == sport]
        
        
    merged2 = pd.merge(mydata, n_medals2, how="left", on=["id"]).sort_values(by=["placement", "number_medals"], ascending=[True, False])
    
    tableData = merged2.drop_duplicates(["id"])
    
    fig = go.Figure(data=[go.Table(
        columnwidth = [21,7,18,18,18,18],
        header=dict(values=["Name", "Gender", "Birthday", "Deathday",
                            "Place of birth","Place of death"],
                            line_color='black',
                            fill_color='royalblue',
                            font_color='white',
                            font_weight='bold',
                            align='left'),
        cells=dict(values=[tableData.name, tableData.gender, tableData.date_of_birth, 
                           tableData.date_of_death, tableData.place_of_birth,
                           tableData.place_of_death],
                           line_color='black',
                           fill_color='cornflowerblue',
                           align='left'))
    ],
    layout=go.Layout(title='Personal information about each medalist',
                     font_color='black',
                     paper_bgcolor='lightblue'))
    
    return fig

@app.callback(
    Output(component_id='wordcloud', component_property='list'),
    Output(component_id='discipline_table', component_property='figure'),
    Output(component_id='wordcloud', component_property="style"),
    Output(component_id='discipline_table', component_property="style"),
    [
        Input(component_id='medal_color', component_property='value'),
        Input(component_id='medal_chart', component_property='clickData'),
        Input(component_id='wordcloud', component_property='click'),
    ],
)
    
def display_wordcloud(medal_color,clickData,click_word):
                    
        mydata = filter_data(medal_color)
        
        event = None
        if clickData != None:
            event = clickData["points"][0]["x"]
            mydata = mydata[mydata["year"] == event]
        
        words = {}
        word_data = mydata.drop_duplicates(["discipline","medal_color","year","gender"])
        sportdata = word_data['sport']

        for k in sportdata: 
            if k in words.keys(): 
                words[k] += 1
            
            else:
                words[k] = 1

        sport = None
        if click_word != None:
            sport = click_word[0] 
            mydata = mydata[mydata['sport'] == sport]

            merged2 = mydata.sort_values(by=["discipline"])

            fig = go.Figure(data=[go.Table(
                columnwidth = [25,35,20,20],
                header=dict(values=["Discipline","Name", "Medal Color", "Olympic Event"],
                                    line_color='black',
                                    fill_color='royalblue',
                                    font_color='white',
                                    font_weight='bold',
                                    align='left'),
                cells=dict(values=[merged2.discipline, merged2.name,
                                   merged2.medal_color, merged2.year],
                                   line_color='black',
                                   fill_color='cornflowerblue',
                                   align='left'))
                ],layout=go.Layout(title="Disciplines of "+sport,
                                   font_color='black',
                                   paper_bgcolor='lightblue'))
            return [], fig, {"display":"none"}, {"display":"block"}
        else:
            wordData = []
            for sport, count in words.items():
                wordData.append([sport, count, sport + ": " + str(count) + " medals"])
            return wordData, {}, {"display":"block"}, {"display":"none"}

@app.callback(
    Output(component_id='medal_chart', component_property='figure'),
    [
        Input(component_id='medal_color', component_property='value'),
        Input(component_id='wordcloud', component_property='click'),
    ]
)
def display_chart(medal_color, click_word):
 
    mydata = filter_data(medal_color)
    
    sport = None
    if click_word != None: 
        sport = click_word[0] 
        mydata = mydata[mydata['sport'] == sport]

    mydata = mydata.drop_duplicates(["discipline","medal_color","gender"])
    medal_counts = mydata.groupby(by=["year"]).size().reset_index(name="counts")

    
    fig = px.bar(medal_counts, x='year', y='counts',
                 title="Number of medals won each olympic event",
                 labels={ # Change default labels
                "counts": "Number of Medals Won",  "year": "Olympic events"},
                template='seaborn')
    fig.update_layout(plot_bgcolor='lightblue',paper_bgcolor='lightblue',font_color='black')
    return fig


@app.callback(
    Output(component_id='medal_color', component_property='value'),
    [
        Input(component_id='resetAll', component_property='n_clicks')
        
    ]
)
def rest(n_clicks):
    return 'All'

@app.callback(
    Output(component_id='medal_chart', component_property='clickData'),
    [
        Input(component_id='resetAll', component_property='n_clicks'),
        Input(component_id='resetBar', component_property='n_clicks')
    ]
)
def restclickData(n_clicks,n_clicks2):
        return None

@app.callback(
    Output(component_id='wordcloud', component_property='click'),
    [
        Input(component_id='resetAll', component_property='n_clicks'),
        Input(component_id='resetCloud', component_property='n_clicks')
    ]
)
def restclickData2(n_clicks,n_clicks2):
        return None


if __name__ == '__main__':
    app.run_server(debug=False, port=8014)