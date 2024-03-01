from bs4 import BeautifulSoup
import requests
import pandas as pd

def get_soup(html_link):
    r = requests.get(html_link)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

def get_links(soup):
    links = []
    for a in soup.find_all('a', href=True):
        link = a['href']
        if 'L2MReport.html' in link:
            links.append(a)
    expanded_links = []
    for link in links:
        expanded_links.append((link['href'], link.get_text()))
    return expanded_links

def get_game_link_data(expanded_links):
    df = pd.DataFrame(expanded_links, columns = ['game_link', 'game_score'])

    #Had to fix 2 game_score's which had an extra comma in it when we scraped it. typical kinda messy data cleaning. 

    ix = df[df['game_link'] =='https://official.nba.com/l2m/L2MReport.html?gameId=0022201014'].index
    df.loc[ix, 'game_score'] = 'Nets 122, Nuggets 120'

    ix = df[df['game_link'] =='https://official.nba.com/l2m/L2MReport.html?gameId=0022200598'].index
    df.loc[ix, 'game_score'] = 'Pacers 116, Hornets 111'

    blazer_games = df[df['game_score'].apply(lambda x: 'trail' in x.lower())]['game_score']
    df.loc[blazer_games.index, 'game_score'] = blazer_games.apply(lambda x: x.replace('Trail Blazers', 'Trailblazers'))

    df['team_1_score'] = df['game_score'].apply(lambda x: x.split(',')[0].strip())
    df['team_2_score'] = df['game_score'].apply(lambda x: x.split(',')[1].strip())

    df['team_1_name' ] = df['team_1_score'].apply(lambda x: x.split(" ")[0].strip())
    df['team_1_score' ] = df['team_1_score'].apply(lambda x: x.split(" ")[1].strip())

    df['team_2_name' ] = df['team_2_score'].apply(lambda x: x.split(" ")[0].strip())
    df['team_2_score' ] = df['team_2_score'].apply(lambda x: x.split(" ")[1].strip())
    
    df['game_id'] = df['game_link'].apply(lambda x: x.split('?')[1].split('=')[1])
    df['game_id'] = df['game_id'].apply(lambda x: x.split('%')[0])
    
    return df

if __name__ == '__main__':
    nba_22_23 = 'https://official.nba.com/2022-23-nba-officiating-last-two-minute-reports/'
    nba_23_24 = 'https://official.nba.com/2023-24-nba-officiating-last-two-minute-reports/'
    soup = get_soup(nba_22_23)
    expanded_links = get_links(soup)
    df = get_game_link_data(expanded_links)
    df.to_csv('../data/nba_22_23_l2m_metadata.csv', index=False)
    soup = get_soup(nba_23_24)
    expanded_links = get_links(soup)
    df = get_game_link_data(expanded_links)
    df.to_csv('../data/nba_23_24_l2m_metadata.csv', index=False)