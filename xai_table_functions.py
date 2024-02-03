import plotly.graph_objects as go
def plot_data_with_hyperlinks(data):
    fig = go.Figure(
        data=[
            go.Table(
                columnwidth=[0.8, 0.8, 1, 3],
                header=dict(
                    values=[f"<b>{i}</b>" for i in data.columns.to_list()],
                    fill_color='lightskyblue',
                    font=dict(color='black', size=15)
                ),
                cells=dict(
                    values=data.transpose(),
                    fill_color='rgb(239, 243, 255)',
                    font=dict(color='black', size=13)),
            )
        ]
    )
    return fig


def filter_dataframe(data, framework=None, dtype=None):
    if framework and dtype:
        to_schow = data[(data['Framework'].apply(lambda x: True if framework in x else False)) & (
            data['DataType'].apply(lambda x: True if dtype in x else False))]

    elif framework:
        to_schow = data[data['Framework'].apply(lambda x: True if framework in x else False)]


    elif dtype:
        to_schow = data[data['DataType'].apply(lambda x: True if dtype in x else False)]

    return to_schow
