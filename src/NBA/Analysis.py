# -*- coding:utf-8 -*-
import pandas as pd
import math
import csv
import random
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import cross_val_score

# 当每支队伍没有elo等级分时，赋予其基础elo等级分
base_elo = 1600
team_elos = {}
team_stats = {}
X = []
y = []
# 存放数据的目录
folder = 'data'


def initialize_data(Mstat, Ostat, Tstat):
    new_Mstat = Mstat.drop(['Rk', 'Arena'], axis=1)
    new_Ostat = Ostat.drop(['Rk', 'G', 'MP'], axis=1)
    new_Tstat = Tstat.drop(['Rk', 'G', 'MP'], axis=1)

    team_stats1 = pd.merge(new_Mstat, new_Ostat, how='left', on='Team')
    team_stats1 = pd.merge(team_stats1, new_Tstat, how='left', on='Team')
    return team_stats1.set_index('Team', inplace=False, drop=True)


def get_elo(team):
    try:
        return team_elos[team]
    except:
        # 当最初没有 elo 时，给每个队伍赋最初的 base_elo
        team_elos[team] = base_elo
        return team_elos[team]


# 计算每个球队的elo值
def calc_elo(win_team, lose_team):
    winner_rank = get_elo(win_team)
    loser_rank = get_elo(lose_team)

    rank_diff = winner_rank - loser_rank
    exp = (rank_diff * -1) / 400
    odds = 1 / (1 + math.pow(10, exp))

    # 根据rank级别修改K值
    if winner_rank < 2100:
        k = 32
    elif 2100 <= winner_rank < 2400:
        k = 24
    else:
        k = 16

    # 胜者评分升高，败者评分降低
    new_winner_rank = round(winner_rank + (k * (1 - odds)))
    new_rank_diff = new_winner_rank - winner_rank
    new_loser_rank = loser_rank - new_rank_diff

    return new_winner_rank, new_loser_rank


def build_data_set(all_data):
    print("Building data set..")
    X = []
    skip = 0
    for index, row in all_data.iterrows():
        wteam = row['WTeam']
        lteam = row['LTeam']

        # 获取最初的elo值
        win_team_elo = get_elo(wteam)
        lose_team_elo = get_elo(lteam)

        # 给主场比赛的队伍加上100的elo值
        if row['WLoc'] == 'H':
            win_team_elo += 100
        else:
            lose_team_elo += 100

        # 把elo作为评价每个队伍的第一个特征值
        win_team_features = [win_team_elo]
        lose_team_features = [lose_team_elo]

        # 添加从basketball reference.com获得的每个队伍的统计信息
        for key, value in team_stats.loc[wteam].iteritems():
            win_team_features.append(value)
        for key, value in team_stats.loc[lteam].iteritems():
            lose_team_features.append(value)

        # 将两只队伍的特征值随机的分配在每次比赛数据的左右两侧
        # 并将对应的0/1赋给y值
        if random.random() > 0.5:
            X.append(win_team_features + lose_team_features)
            y.append(0)
        else:
            X.append(lose_team_features + win_team_features)
            y.append(1)

        if skip == 0:
            print('X', X)
            skip = 1

        # 根据这场比赛的数据更新队伍的elo值
        new_winner_rank, new_loser_rank = calc_elo(wteam, lteam)
        team_elos[wteam] = new_winner_rank
        team_elos[lteam] = new_loser_rank

    return np.nan_to_num(X), y


def predict_winner(team_1, team_2, model):
    features = []

    # team_1，客场队伍
    features.append(get_elo(team_1))
    for key, value in team_stats.loc[team_1].iteritems():
        features.append(value)

    # team_2，主场队伍
    features.append(get_elo(team_2) + 100)
    for key, value in team_stats.loc[team_2].iteritems():
        features.append(value)

    features = np.nan_to_num(features)
    return model.predict_proba([features])


if __name__ == 'main':

    Mstat = pd.read_csv(folder + '/15-16Miscellaneous_Stat.csv')
    Ostat = pd.read_csv(folder + '/15-16Opponent_Per_Game_Stat.csv')
    Tstat = pd.read_csv(folder + '/15-16Team_Per_Game_Stat.csv')

    team_stats = initialize_data(Mstat, Ostat, Tstat)

    result_data = pd.read_csv(folder + '/2015-2016_result.csv')
    X, y = build_data_set(result_data)

    # 训练网络模型
    print("Fitting on %d game samples.." % len(X))

    model = linear_model.LogisticRegression()
    model.fit(X, y)

    # 利用10折交叉验证计算训练正确率
    print("Doing cross-validation..")
    print(cross_val_score(model, X, y, cv=10, scoring='accuracy', n_jobs=-1).mean())

    # 利用训练好的model在16-17年的比赛中进行预测
    print('Predicting on new schedule..')
    schedule1617 = pd.read_csv(folder + '/16-17Schedule.csv')
    result = []
    for index, row in schedule1617.iterrows():
        team1 = row['Vteam']
        team2 = row['Hteam']
        pred = predict_winner(team1, team2, model)
        prob = pred[0][0]
        if prob > 0.5:
            winner = team1
            loser = team2
            result.append([winner, loser, prob])
        else:
            winner = team2
            loser = team1
            result.append([winner, loser, 1 - prob])

    with open('16-17Result.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['win', 'lose', 'probability'])
        writer.writerows(result)
        print('done.')
