# tastediveW
a python tastedive wrapper with limited functionality

## Features
* using publically available API to query title information
* fetch stats for titles
* download or export userdata

## Limitations
* currently only support querying existing items, adding new items are currently planned

## Planned
* supporting queries with graphQL

## Documentation

### 1. querying data
```py
from tastediveW import Title

title = Title.getTitle("Cyberpunk-2077")
pprint(title)
```

```sh
GameTitle(name='Cyberpunk 2077',
          slug_name='cyberpunk-2077',
          description='Cyberpunk 2077 is an action role-playing video game '
                      'developed and published by CD Projekt. The story takes '
                      'place in Night City, an open world set in the Cyberpunk '
                      'universe. Players assume the first-person perspective '
                      'of a customisable mercenary known as V, who can acquire '
                      'skills in hacking and machinery with options for melee '
                      "and ranged combat; the story follows V's struggles to "
                      'deal with a mysterious cybernetic implant that '
                      "threatens to overwrite V's body with the personality "
                      'and memories of a man who died decades ago. As the '
                      'player explores Night City and performs various '
                      'missions, V uncovers the origins of the device and the '
                      'man encoded upon it, who now appears as a specter only '
                      'the player can hear or see; the two must work together '
                      "if there is any hope to separate the two and save V's "
                      'life.',
          youtube_url='https://www.youtube-nocookie.com/embed/BO8lX3hDU30',
          youtube_clipid='BO8lX3hDU30',
          wikipedia_url='http://en.wikipedia.org/wiki/Cyberpunk_2077',
          qid=None,
          category='games',
          _ratings=None)
```

### 2. getting similar titles
(coninuing previous codeblock)
```py
for s in title.similar:
    print(str(s))
```

```
<games> biomutant
<games> anthem
<games> pathfinder-wrath-of-the-righteous
<games> mass-effect-andromeda
<games> final-fantasy-vii-remake-intergrade
<games> diablo-ii-resurrected
<games> godfall
<games> kingdom-come-deliverance
<games> greedfall
<games> disco-elysium-the-final-cut
<games> dragon-ball-z-kakarot
<games> nioh-2
<games> kingdoms-of-amalur-re-reckoning
<games> new-world
<games> nier-automata-game-of-the-yorha-edition
<games> nier-replicant-ver-1-22474487139
<games> final-fantasy-vii-remake
<games> the-outer-worlds
<games> persona-5-strikers
<games> monster-hunter-world-iceborne
```
### 2.5. setting up cookies
```py
from tastediveW import auth
    
with open("config.json") as f:
    json_data = json.load(f)

auth.setCookies(json_data)
```
1. auth.setCookies supports both passing str and dict
2. it is possible to use modules such as `browsercookie` and pass it into setCookies
3. `_csrf_token` will be automatically generated using `bs4` webscrapping

### 3. get stats of a title
> if a title is initialized from Account.load(), method simple_stat will be directly available as a str

> in all other scenarios, it will first fetch from standard web scrapping
(coninuing previous codeblock)
```python
rating = title.ratings
pprint(rating)
```
```
Ratings(
    title=...
    likes=175,
    mehs=39,
    dislikes=26,
    is_like=False,
    is_meh=False,
    is_dislike=True,
    _entity_id='89192',
    last_fetched=...,
    saved_lists=[],
    expired=False
)
```

> if cookies are properly set, it is then possible to call `like()`, `meh()`, `dislike()`

> `TasteList` can only be initialized from ratings currently