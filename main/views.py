from django.shortcuts import render
import pandas as pd
import numpy as np
import joblib
import random


# Assuming data is loaded as in your original code snippet
data = pd.read_csv(r"C:\Users\PMLS\Desktop\footballproject\football\All Matches.csv")
data["Result"]= np.where(data["HomeTeamGoals"] > data["AwayTeamGoals"], "Home Team Wins", np.where(data["HomeTeamGoals"] < data["AwayTeamGoals"], "Away Team Wins", "Draw"))
data['home_team_avg_goals_scored'] = data.groupby('HomeTeamName')['HomeTeamGoals'].transform(lambda x: x.rolling(window=10, min_periods=1).mean())
data['home_team_avg_goals_conceded'] = data.groupby('HomeTeamName')['AwayTeamGoals'].transform(lambda x: x.rolling(window=10, min_periods=1).mean())
data['away_team_avg_goals_scored'] = data.groupby('AwayTeamName')['AwayTeamGoals'].transform(lambda x: x.rolling(window=10, min_periods=1).mean())
data['away_team_avg_goals_conceded'] = data.groupby('AwayTeamName')['HomeTeamGoals'].transform(lambda x: x.rolling(window=10, min_periods=1).mean())


def home(request):
    x=""
    y=""
    if request.method == "POST":
        awayteam = request.POST.get("away-team")
        hometeam = request.POST.get("home-team")
        year = request.POST.get("year")
        
        future_matches = pd.DataFrame({
            'AwayTeamName': [awayteam],
            'HomeTeamName': [hometeam],
            'Year': [year]
        })

        # Function to get average goals or return None if team not found
        def get_avg_goals(team_name, avg_goals_column):
            if team_name in data['HomeTeamName'].unique():
                return data[data['HomeTeamName'] == team_name][avg_goals_column].iloc[-1]
            else:
                return None

        # Apply function to get average goals scored and conceded for home and away teams
        future_matches['home_team_avg_goals_scored'] = future_matches['HomeTeamName'].apply(lambda x: get_avg_goals(x, 'home_team_avg_goals_scored'))
        future_matches['home_team_avg_goals_conceded'] = future_matches['HomeTeamName'].apply(lambda x: get_avg_goals(x, 'home_team_avg_goals_conceded'))
        future_matches['away_team_avg_goals_scored'] = future_matches['AwayTeamName'].apply(lambda x: get_avg_goals(x, 'away_team_avg_goals_scored'))
        future_matches['away_team_avg_goals_conceded'] = future_matches['AwayTeamName'].apply(lambda x: get_avg_goals(x, 'away_team_avg_goals_conceded'))
        x=get_avg_goals(x, 'home_team_avg_goals_scored')
        y=get_avg_goals(x, 'away_team_avg_goals_conceded')
        print(x,y)
        

        # Load model and predict results
        if x=! None and y!=None:
            model = joblib.load("model (1).pkl")
            features = ['home_team_avg_goals_scored', 'home_team_avg_goals_conceded', 'away_team_avg_goals_scored', 'away_team_avg_goals_conceded', 'Year']
            future_predictions = model.predict(future_matches[features])
            future_matches['predicted_result'] = future_predictions

            # Determine winner based on predicted result
            future_matches['Winner'] = np.where(future_matches['predicted_result'] == 'Home Team Wins', future_matches['HomeTeamName'], future_matches['AwayTeamName'])
            winner = future_matches['Winner'].iloc[0]  
        else:
            print("hi")
            winner=random.choice([hometeam,awayteam])
            
          
            
        # Render template with results
        return render(request, "index.html",locals())

    # Render initial form
    return render(request, "index.html")
