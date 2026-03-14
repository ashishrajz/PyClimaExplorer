import plotly.express as px


def plot_heatmap(data):
    fig = px.imshow(
        data,
        color_continuous_scale="RdBu_r",
        origin="lower"
    )

    fig.update_layout(
        title="Global Climate Map",
        xaxis_title="Longitude",
        yaxis_title="Latitude"
    )

    return fig