import dash
import dash_core_components as dcc
import dash_table
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import numpy as np


def get_lowest_uninjured_on_field_score_for_position(row):
    team_id = row["Team ID"]
    round_id = row["Round_x"]
    position = row["pos"]
    comparison_player = df_match_data_with_fanfooty_info.loc[
        (df_match_data_with_fanfooty_info["Team ID"] == team_id)
        & (df_match_data_with_fanfooty_info["Round_x"] == round_id)
        & (df_match_data_with_fanfooty_info["pos"] == position)
        & (df_match_data_with_fanfooty_info["Round_x"] <= 21)
        & (df_match_data_with_fanfooty_info["On Field?"] == True)
        & (df_match_data_with_fanfooty_info["pts"] > 0)
        & (df_match_data_with_fanfooty_info["Injured"] == False)
    ]
    comparison_player = comparison_player.nsmallest(1, "pts")
    comparison_player = comparison_player.iloc[0]
    return_data = {
        "Full Name": comparison_player["Full Name_x"],
        "pts": comparison_player["pts"],
    }
    return return_data


# Dataframes, spaces between elements

df_final_standings = pd.read_csv("inputs/2019 final standings.csv")
df_final_standings = df_final_standings.loc[:, ["rank", "Team Name"]]

df_final_ladder = pd.read_csv("inputs/2019_final_ladder.csv")

df_fixture_results = pd.read_csv("inputs/fixture_combined_rank.csv")

df_top_10_scores = df_fixture_results
df_top_10_scores["Rank"] = df_top_10_scores["Points"].rank(ascending=False)
df_top_10_scores = df_top_10_scores.sort_values("Rank").head(10)
df_top_10_scores = df_top_10_scores[
    ["Round", "Team Name", "Points", "Opponent Team Name", "Opponent Points"]
]

df_fixture_difficulty = (
    df_fixture_results.groupby("Team Name")["Opponent Rank"]
    .agg("mean")
    .sort_values(ascending=True)
)
df_fixture_difficulty = df_fixture_difficulty.reset_index()
df_fixture_difficulty["Opponent Rank"] = df_fixture_difficulty["Opponent Rank"].round(1)

df_combined_weekly_ladders = pd.read_csv("inputs/weekly_ladder - with finals.csv")
df_injury_list = pd.read_csv("inputs/injury_list.csv")
df_most_total_injuries = (
    df_injury_list.groupby(["Team Name"])["pts"]
    .agg(["mean", "count"])
    .sort_values("count", ascending=False)
)
df_most_total_injuries = df_most_total_injuries.reset_index()

df_donut_list = pd.read_csv("inputs/donut_list.csv")
df_donut_summary = df_donut_list.groupby(by="Team Name")["Full Name"].agg(["count"])
df_donut_summary = df_donut_summary.reset_index().sort_values("count", ascending=False)

df_all_league_match_data = pd.read_csv("inputs/all_matches_detailed.csv").sort_values(
    ["Round", "Match Name", "Team ID", "On Field?", "pos", "pts"],
    ascending=[True, True, True, False, True, False],
)

unique_player_data = df_all_league_match_data.loc[
    (df_all_league_match_data["Round"] <= 21)
    & (df_all_league_match_data["On Field?"] == True)
]
unique_player_count_pivot = (
    unique_player_data.pivot_table(
        index="Team Name", values=("id"), aggfunc=lambda x: len(x.unique())
    )
    .sort_values(by=["id"], ascending=False)
    .reset_index()
)

bench_list = df_all_league_match_data.loc[
    (df_all_league_match_data["Round"] <= 21)
    & (~df_all_league_match_data["On Field?"] == True)
].replace(0, np.NaN)
scoring_bench_player_count = bench_list.groupby(["Team Name"])["pts"].agg(
    ["mean", "count"]
)
scoring_bench_player_count = scoring_bench_player_count.reset_index().rename(
    columns={"Team Name": "Team Name", "count": "Scoring Players", "mean": "Average"}
)
scoring_bench_player_count["Utilisation"] = (
    scoring_bench_player_count["Scoring Players"] / 84
) * 100
scoring_bench_player_count["Utilisation"] = round(
    scoring_bench_player_count["Utilisation"], 1
)
scoring_bench_player_count = scoring_bench_player_count.sort_values(
    by=["Utilisation"], ascending=False
)

df_match_data_with_fanfooty_info = pd.read_csv(
    r"inputs/df_match_data_with_fanfooty_info.csv"
)
bench_list_2 = df_match_data_with_fanfooty_info.loc[
    (df_match_data_with_fanfooty_info["Round_x"] <= 21)
    & (~df_match_data_with_fanfooty_info["On Field?"] == True)
    & (df_match_data_with_fanfooty_info["pts"] > 0)
    & (df_match_data_with_fanfooty_info["Injured"] == False)
]
bench_list_2["Played..."] = bench_list_2.apply(
    lambda row: get_lowest_uninjured_on_field_score_for_position(row)["Full Name"],
    axis=1,
)
bench_list_2["Actually got..."] = bench_list_2.apply(
    lambda row: get_lowest_uninjured_on_field_score_for_position(row)["pts"], axis=1
)
bench_list_2["Diff"] = bench_list_2["pts"] - bench_list_2["Actually got..."]
df_highest_bench_diff = bench_list_2.nlargest(10, "Diff")[
    [
        "Round_x",
        "Match Name",
        "Team Name",
        "Full Name_x",
        "pts",
        "Played...",
        "Actually got...",
        "Diff",
    ]
]

# All elements used in Dash Body
el_final_standings = dbc.Col(
    [
        html.H4(children="Final Standings"),
        html.Div(
            children=[
                dash_table.DataTable(
                    id="final-standings-table",
                    columns=[{"name": i, "id": i} for i in df_final_standings.columns],
                    data=df_final_standings.to_dict("records"),
                ),
            ],
            style={"textAlign": "center"},
        ),
    ],
    width=4,
)
el_ladder = dbc.Col(
    [
        html.H4(children="End of regular season ladder"),
        html.Div(
            children=[
                dash_table.DataTable(
                    id="end-ladder-table",
                    columns=[{"name": i, "id": i} for i in df_final_ladder.columns],
                    data=df_final_ladder.to_dict("records"),
                ),
            ],
        ),
    ],
    width=8,
)
el_ladder_tracker = dbc.Col(
    [
        dcc.Graph(
            figure={
                "data": [
                    dict(
                        x=df_combined_weekly_ladders[
                            df_combined_weekly_ladders["Team Name"] == i
                        ]["Round"],
                        y=df_combined_weekly_ladders[
                            df_combined_weekly_ladders["Team Name"] == i
                        ]["rank_number"],
                        name=i,
                        line=dict(width=5),
                    )
                    for i in df_combined_weekly_ladders["Team Name"].unique()
                ],
                "layout": {
                    "title": "Ladder Tracker",
                    "yaxis": {"autorange": "reversed"},
                },
            },
        ),
    ],
)
el_team_scoring_summary_boxplot = dbc.Col(
    [
        dcc.Graph(
            figure={
                "data": [
                    go.Box(
                        dict(
                            y=df_fixture_results[df_fixture_results["Team Name"] == i][
                                "Points"
                            ],
                            name=i,
                        )
                    )
                    for i in df_fixture_results["Team Name"].unique()
                ],
                "layout": {"title": "Team Scoring Summary"},
            }
        ),
    ],
)
el_top_10_scores = dbc.Col(
    [
        html.H4(children="Top 10 Scores"),
        html.Div(
            children=[
                dash_table.DataTable(
                    id="top-10-scores-table",
                    columns=[{"name": i, "id": i} for i in df_top_10_scores.columns],
                    data=df_top_10_scores.to_dict("records"),
                ),
            ],
            style={"textAlign": "center"},
        ),
    ],
    width=6,
    align="center",
)
el_donut_count = dbc.Col(
    [
        dcc.Graph(
            figure={
                "data": [
                    go.Bar(
                        y=df_donut_summary["Team Name"],
                        x=df_donut_summary["count"],
                        text=df_donut_summary["count"],
                        textposition="auto",
                        orientation="h",
                        hoverinfo="y",
                    ),
                ],
                "layout": {
                    "title": "Number of Donuts",
                    "margin": dict(l=150),
                    "yaxis": {"autorange": "reversed"},
                },
            },
        )
    ]
)
el_hardest_fixture = dbc.Col(
    [
        dcc.Graph(
            figure={
                "data": [
                    go.Bar(
                        y=df_fixture_difficulty["Team Name"],
                        x=df_fixture_difficulty["Opponent Rank"],
                        text=df_fixture_difficulty["Opponent Rank"],
                        textposition="auto",
                        orientation="h",
                        hoverinfo="y",
                    ),
                ],
                "layout": {
                    "title": "Hardest Fixture (Average opponent score rank)",
                    "margin": dict(l=150),
                    "yaxis": {"autorange": "reversed"},
                },
            },
        )
    ],
    width=6,
)
el_number_of_injuries = dbc.Col(
    [
        dcc.Graph(
            figure={
                "data": [
                    go.Bar(
                        y=df_most_total_injuries["Team Name"],
                        x=df_most_total_injuries["count"],
                        text=df_most_total_injuries["count"],
                        textposition="auto",
                        orientation="h",
                        hoverinfo="y",
                    ),
                ],
                "layout": {
                    "title": "Number of in-game Injuries",
                    "margin": {"l": 150},
                    "yaxis": {"autorange": "reversed"},
                },
            },
        ),
    ],
    width=6,
)
el_number_of_onfield_players = dbc.Col(
    [
        dcc.Graph(
            figure={
                "data": [
                    go.Bar(
                        y=unique_player_count_pivot["Team Name"],
                        x=unique_player_count_pivot["id"],
                        text=unique_player_count_pivot["id"],
                        textposition="auto",
                        orientation="h",
                        hoverinfo="y",
                    ),
                ],
                "layout": {
                    "title": "Number of Players used on field",
                    "margin": dict(l=150),
                    "yaxis": {"autorange": "reversed"},
                },
            },
        ),
    ],
)
el_bench_utilisation = dbc.Col(
    [
        dcc.Graph(
            figure={
                "data": [
                    go.Bar(
                        y=scoring_bench_player_count["Team Name"],
                        x=scoring_bench_player_count["Utilisation"],
                        text=scoring_bench_player_count["Utilisation"],
                        textposition="auto",
                        orientation="h",
                        hoverinfo="y",
                    ),
                ],
                "layout": {
                    "title": "% of players on bench who played",
                    "margin": dict(l=150),
                    "yaxis": {"autorange": "reversed"},
                },
            },
        ),
    ],
)
el_bench_regrets = dbc.Col(
    [
        html.H4(children="Highest bench player to on field player difference"),
        html.Div(
            children=[
                dash_table.DataTable(
                    id="highest-bench-diff-table",
                    columns=[
                        {"name": i, "id": i} for i in df_highest_bench_diff.columns
                    ],
                    data=df_highest_bench_diff.to_dict("records"),
                ),
            ],
        ),
    ],
)

# Dash Body
body = dbc.Container(
    [
        html.H1("Addicts Supercoach League - 2019 Summary"),
        html.Br(),
        dbc.Row([el_final_standings, el_ladder,]),
        dbc.Row([el_ladder_tracker,]),
        dbc.Row([el_team_scoring_summary_boxplot,],),
        dbc.Row([el_top_10_scores, el_donut_count],),
        dbc.Row([el_hardest_fixture, el_number_of_injuries,],),
        dbc.Row([el_number_of_onfield_players, el_bench_utilisation,],),
        dbc.Row([el_bench_regrets,]),
    ],
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(body, style={"text-align": "center",})

if __name__ == "__main__":
    app.run_server(debug=True)
