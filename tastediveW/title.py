
from dataclasses import dataclass
import dataclasses
from functools import cached_property
import typing
from slugify import slugify
from tastediveW.auth import makeRequest
from tastediveW.rating import Ratings

class _TitleClsMethods:
    @staticmethod
    def fromQid(qid : str):
        res = makeRequest(url=f"https://tastedive.com/?qid={qid}")
        name = res.url.rsplit("/", 1)[-1]
        return name

    @staticmethod
    def _api_query(queryName : str, info : bool = True, category : str = None, limit : int = None):

        url = f"https://tastedive.com/api/similar?q={queryName}"

        if info:
            url += "&info=1"

        if category:
            url += f"&type={category}"
        
        if limit:
            url += f"&limit={limit}"

        results = makeRequest(
            url=url
        )
        try:
            data = results.json()
        except:
            raise ValueError("Invalid JSON")

        baseTitleData = data["Similar"]["Info"][0]
        data = data.get("Similar")
        data = data.get("Results")

        similarLists = data

        return baseTitleData, similarLists

    @classmethod
    def _parse_title(cls, title, category : str = None, limit : int = None):
        queryName = title if isinstance(title, str) else title.slug_name
        baseTitle = None
        if isinstance(title, Title):
            baseTitle = title

        baseTitleData, similarLists = cls._api_query(queryName, category=category, limit=limit)

        if baseTitle is None:
            baseTitle = Title.fromDict(**baseTitleData)

        ret = []
        for d in similarLists:
            ret.append(Title.fromDict(baseTitle,**d))

        return ret, baseTitle

    @classmethod
    def getSimilar(
        cls, 
        title : typing.Union['Title', str], 
        category : typing.Literal["music","movies","shows","podcasts","books", "authors","games"] = None, 
        limit : int = None
    ) -> typing.List['Title']:
        ret, baseTitle = cls._parse_title(title, category, limit)
        return ret

    @classmethod
    def getTitle(
        cls, 
        title : str, 
        category : typing.Literal["music","movies","shows","podcasts","books", "authors","games"] = None, 
        limit : int = None
    ):
        ret, baseTitle = cls._parse_title(title, category, limit)
        return baseTitle

class TitleMeta(type):
    _instances = {}
    _similar = {}

    def __call__(cls, *args, **kwargs):

        slug_name = kwargs.get("slug_name")
        if slug_name is None:
            raise ValueError("slug_name must be set")

        if slug_name not in cls._instances:
            cls._instances[slug_name] = super().__call__(**kwargs)
            instance = cls._instances[slug_name]
        else:
            instance = cls._instances[slug_name]
            # setattr for all kwargs
            for k, v in kwargs.items():
                if v is None:
                    continue
                object.__setattr__(instance, k, v)
            return instance

        if slug_name not in cls._similar:
            cls._similar[instance] = []

        remove = []
        for arg in args:
            if isinstance(arg, Title):
                cls._addSimilar(instance, arg)
                cls._addSimilar(arg, instance)
                remove.append(arg)
            else:
                raise ValueError("args must be instances of Title")

        return instance

    def _addSimilar(cls, host, similar):
        if host not in cls._similar:
            cls._similar[host] = []

        if similar in cls._similar[host]:
            return

        cls._similar[host].append(similar)


@dataclass(frozen=True)
class Title(_TitleClsMethods, metaclass=TitleMeta):
    name : str
    slug_name : str
    description : str = None
    youtube_url : str = None
    youtube_clipid : str = None
    wikipedia_url : str = None
    qid : str =  None
    category : str = None
    _ratings : typing.Literal["like", "meh", "dislike"] = None

    def refetch(self):
        self.getTitle(self.slug_name)

    @property
    def simple_rating(self):
        return self._ratings

    @property
    def ratings(self):
        if not hasattr(self, "_ratings") or isinstance(self._ratings, str):
            object.__setattr__(self, "_ratings", None)

        self._ratings : Ratings

        if self._ratings is None:
            object.__setattr__(self, "_ratings", Ratings.fromTitle(self))
        else:
            self._ratings._checkExpire()
            if self._ratings.expired:
                object.__setattr__(self, "_ratings", Ratings.fromTitle(self))

        return self._ratings

    @classmethod
    def fromDict(cls, *args, **kwargs) -> 'Title':
        if cls != Title:
            names = [k.name for k in dataclasses.fields(cls)]
            kwargs = {k: v for k, v in kwargs.items() if k in names}

            return cls(*args, **kwargs)

        category = kwargs.pop("Type", None)
        description = kwargs.pop("wTeaser", None)
        name = kwargs.pop("Name", None)
        youtube_url = kwargs.pop("yUrl", None)
        youtube_clipid = kwargs.pop("yID", None)
        wikipedia_url = kwargs.pop("wUrl", None)

        if name is None:
            raise ValueError("No Name provided")

        slug_name = slugify(name)

        new_kws = {
            "description" : description,
            "name" : name,
            "youtube_url" : youtube_url,
            "youtube_clipid" : youtube_clipid,
            "wikipedia_url" : wikipedia_url,
            "slug_name" : slug_name
        }

        new_kws = {k: v for k, v in new_kws.items() if v is not None}


        match category:
            case "movie" | "movies":
                return MovieTitle.fromDict(*args, **new_kws, **kwargs)
            case "tv" | "tv show" | "tv shows":
                return TvTitle.fromDict(*args, **new_kws, **kwargs)
            case "book" | "books":
                return BookTitle.fromDict(*args, **new_kws, **kwargs)
            case "game" | "games":
                return GameTitle.fromDict(*args, **new_kws, **kwargs)
            case "author" | "authors":
                return AuthorTitle.fromDict(*args, **new_kws, **kwargs)
            case "music":
                return MusicTitle.fromDict(*args, **new_kws, **kwargs)
            case "podcast | podcasts":
                return PodcastTitle.fromDict(*args, **new_kws, **kwargs)

        raise ValueError("Unknown category: {}".format(category))

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, Title):
            return False

        return self.slug_name == obj.slug_name

    def __hash__(self) -> int:
        return hash(self.slug_name)

    def __str__(self) -> str:
        return f"<{self.category}> {self.slug_name}"

    def __repr__(self) -> str:
        return f"<{self.category}> {self.slug_name}"

    @property
    def similar(self) -> typing.Tuple['Title']:
        similar_list = self.__class__._similar.get(self, [])
        return tuple(similar_list)

@dataclass(frozen=True)
class GameTitle(Title):
    category : str = "games"

@dataclass(frozen=True)
class MusicTitle(Title):
    category : str = "music"

@dataclass(frozen=True)
class MovieTitle(Title):
    category : str = "movies"

@dataclass(frozen=True)
class BookTitle(Title):
    category : str = "books"

@dataclass(frozen=True)
class AuthorTitle(Title):
    category : str = "authors"

@dataclass(frozen=True)
class TvTitle(Title):
    category : str = "shows"

@dataclass(frozen=True)
class PodcastTitle(Title):
    category : str = "podcasts"