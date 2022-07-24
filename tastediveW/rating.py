
from dataclasses import dataclass
import dataclasses
from datetime import datetime, timedelta
import typing
from tastediveW.lists import TasteList
from tastediveW.auth import makeRequest
from bs4 import BeautifulSoup

AUTO_MARK_EXPIRE = False
# 30 min
AUTO_MARK_EXPIRE_TIME = timedelta(minutes=30)

def _resolve_num_string(num_str :str):
    num_str = num_str.replace(",", "").lower()
    if "k" in num_str:
        return int(float(num_str.replace("k", "")) * 1000)
    elif "m" in num_str:
        return int(float(num_str.replace("m", "")) * 1000000)
    elif "b" in num_str:
        return int(float(num_str.replace("b", "")) * 1000000000)
    else:
        return int(num_str)

@dataclass(frozen=True)
class Ratings:
    title : object
    likes : int
    mehs : int
    dislikes : int
    is_like : bool
    is_meh : bool
    is_dislike : bool
    _entity_id : int
    last_fetched : datetime
    saved_lists : typing.Tuple[TasteList] = dataclasses.field(default_factory=tuple)
    expired : bool = False

    def __post_init__(self):
        if self.saved_lists is None:
            object.__setattr__(self, "saved_lists", tuple())

        if len(self.saved_lists) > 0:
            TasteList._resolveAssociateTitles(self.title, *self.saved_lists)
    
    def _checkExpire(self):
        if self.expired:
            return
        if AUTO_MARK_EXPIRE and self.last_fetched + AUTO_MARK_EXPIRE_TIME < datetime.now():
            object.__setattr__(self, "expired", True)

    def simple_rating(self):
        if self.is_like:
            return "like"
        elif self.is_meh:
            return "meh"
        elif self.is_dislike:
            return "dislike"
        else:
            return None

    def like(self):
        if self.is_like:
            return

        res = makeRequest(
            f"https://tastedive.com/profile/add/1/{self._entity_id}",
            params={
                "n" : self.title.slug_name,
            }   
        )
        # if 200
        if res.status_code == 200:
            object.__setattr__(self, "is_like", True)
            object.__setattr__(self, "is_dislike", False)
            object.__setattr__(self, "is_meh", False)

    def meh(self):
        if self.is_meh:
            return
        
        res = makeRequest(
            f"https://tastedive.com/profile/add/4/{self._entity_id}",
            params={
                "n" : self.title.slug_name,
            }   
        )
        # if 200
        if res.status_code == 200:
            object.__setattr__(self, "is_meh", True)
            object.__setattr__(self, "is_like", False)
            object.__setattr__(self, "is_dislike", False)

    def dislike(self):
        if self.is_dislike:
            return
        
        res = makeRequest(
            f"https://tastedive.com/profile/add/2/{self._entity_id}",
            params={
                "n" : self.title.slug_name,
            }   
        )
        # if 200
        if res.status_code == 200:
            object.__setattr__(self, "is_dislike", True)
            object.__setattr__(self, "is_meh", False)
            object.__setattr__(self, "is_like", False)


    def remove(self):
        if not self.is_dislike and not self.is_meh and not self.is_like:
            return

        res = makeRequest(
            f"https://tastedive.com/profile/add/0/{self._entity_id}",
            params={
                "n" : self.title.slug_name,
            }   
        )
        # if 200
        if res.status_code == 200:
            object.__setattr__(self, "is_dislike", False)
            object.__setattr__(self, "is_meh", False)
            object.__setattr__(self, "is_like", False)


    def toggle_lists(self, *tastelists: typing.Tuple[TasteList], skip_existing: bool = False):
        if len(tastelists) == 0:
            return
       
        if skip_existing:
            tastelists = [tastelist for tastelist in tastelists if tastelist not in self.saved_lists]

        for work in tastelists:
            work : TasteList
            res = makeRequest(
                f"https://tastedive.com/profile/list-toggle/{work.id}/{self._entity_id}",
                params={
                    "n" : self.title.slug_name,
                }   
            )
            # if 200
            if res.status_code == 200:
                TasteList._delAssociateTitle(work, self.title)
        
        # set expire
        object.__setattr__(self, "expired", True)

    def remove_all_lists(self):
        return self.toggle_lists(*self.saved_lists)
    

    def expire(self):
        object.__setattr__(self, "expired", True)

    @classmethod
    def fromTitle(cls, title):
        if not hasattr(title, "category") or not hasattr(title, "slug_name"):
            raise ValueError("title must be a Title object")

        res = makeRequest(url=f"https://tastedive.com/{title.category}/like/{title.slug_name}")
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # scope down
        main = soup.find("main")
        article = main.find("article")
        div1 = article.find("div", {"class": "js-entity"})        
        div2 = div1.find("div", {"class": "entity-main has-category-border js-resources-container js-entity-main"})

        entity_div= div1.find("div", {"class": "entity-main__link entity-main__link--description js-resource-card-link"})
        entity_id = entity_div.get("id")

        div3 = div2.find("div", {"class": "entity-main__actions"})        
        entity_opine = div3.find("div", {"class": "entity-opine"})
        div4 = div3.find("div", {"class": "dropdown js-dropdown"})
        tastelists_main = div4.find("ul", {"class": "dropdown__list"})
        tastelists = tastelists_main.find_all("li", {"class": "dropdown__item"})

        buttons = entity_opine.find_all("button")
        count_save = None
        count_like = None
        count_meh = None
        count_dislike = None
        is_saved = False
        is_like = False
        is_meh = False
        is_dislike = False

        list_saved_to = None

        for button in buttons:
            # if has class like
            if button.has_attr("class") and "like" in button["class"]:
                count_like = button.find("span").text
                # aria-pressed = True
                is_like = button.has_attr("aria-pressed") and button["aria-pressed"] == "true"
            elif button.has_attr("class") and "meh" in button["class"]:
                count_meh = button.find("span").text
                # aria-pressed = True
                is_meh = button.has_attr("aria-pressed") and button["aria-pressed"] == "true"
            elif button.has_attr("class") and "dislike" in button["class"]:
                count_dislike = button.find("span").text
                # aria-pressed = True
                is_dislike = button.has_attr("aria-pressed") and button["aria-pressed"] == "true"

        saved_lists = []
        for tastelist in tastelists:
            # id from data-user-list-id
            list_id = tastelist.attrs.get("data-user-list-id")
            # a dropdown__link
            list_name = tastelist.find("a", {"class": "dropdown__link"}).text
            # 
            new_tastelist = TasteList(id=list_id, name=list_name)

            # active marked by dropdown__item--active
            if tastelist.has_attr("class") and "dropdown__item--active" in tastelist["class"]:
                saved_lists.append(new_tastelist)
                
        
        return cls(
            _entity_id=entity_id,
            title=title,
            likes=_resolve_num_string(count_like),
            mehs=_resolve_num_string(count_meh),
            dislikes=_resolve_num_string(count_dislike),
            is_like=is_like,
            is_meh=is_meh,
            is_dislike=is_dislike,
            saved_lists=saved_lists,
            last_fetched = datetime.now()
        )
