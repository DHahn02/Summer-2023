from django.db import models
from django.contrib.auth.admin import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class UserProfile(models.Model):
    class NHL(models.TextChoices):
        NIL = None, "--------------------"
        ANA = "ANA", "Anaheim Ducks"
        ARI = "ARI", "Arizona Coyotes"
        BOS = "BOS", "Boston Bruins"
        BUF = "BUF", "Buffalo Sabres"
        CAL = "CAL", "Calgary Flames"
        CAR = "CAR", "Carolina Hurricanes"
        CHI = "CHI", "Chicago Blackhawks"
        COL = "COL", "Colorado Avalanche"
        CBJ = "CBJ", "Columbus Blue Jackets"
        DAL = "DAL", "Dallas Stars"
        DET = "DET", "Detroit Red Wings"
        EDM = "EDM", "Edmonton Oilers"
        FLA = "FLA", "Florida Panthers"
        LAK = "LAK", "Los Angeles Kings"
        MIN = "MIN", "Minnesota Wild"
        MTL = "MTL", "Montreal Canadiens"
        NSH = "NSH", "Nashville Predators"
        NJD = "NJD", "New Jersey Devils"
        NYI = "NYI", "New York Islanders"
        NYR = "NYR", "New York Rangers"
        OTT = "OTT", "Ottawa Senators"
        PHI = "PHI", "Philadelphia Flyers"
        PIT = "PIT", "Pittsburgh Penguins"
        SJS = "SJS", "San Jose Sharks"
        SEA = "SEA", "Seattle Kraken"
        STL = "STL", "St. Louis Blues"
        TBL = "TBL", "Tampa Bay Lightning"
        TOR = "TOR", "Toronto Maple Leafs"
        VAN = "VAN", "Vancouver Canucks"
        VGK = "VGK", "Vegas Golden Knights"
        WAS = "WAS", "Washington Capitals"
        WPG = "WPG", "Winnipeg Jets"

    class MLB(models.TextChoices):
        NIL = None, "--------------------"
        AZ = "ARI", "Arizona Diamondbacks"
        ATL = "ATL", "Atlanta Braves"
        BAL = "BAL", "Baltimore Orioles"
        BOS = "BOS", "Boston Red Sox"
        CWS = 'CWS', 'Chicago White Sox'
        CHC = "CHC", "Chicago Cubs"
        CIN = "CIN", "Cincinnati Reds"
        CLE = "CLE", "Cleveland Guardians"
        COL = "COL", "Colorado Rockies"
        DET = "DET", "Detroit Tigers"
        HOU = "HOU", "Houston Astros"
        KC = "KCR", "Kansas City Royals"
        LAA = "LAA", "Los Angeles Angels"
        LAD = "LAD", "Los Angeles Dodgers"
        MIA = "MIA", "Miami Marlins"
        MIL = "MIL", "Milwaukee Brewers"
        MIN = "MIN", "Minnesota Twins"
        NYM = "NYM", "New York Mets"
        NYY = "NYY", "New York Yankees"
        OAK = "OAK", "Oakland Athletics"
        PHI = "PHI", "Philadelphia Phillies"
        PIT = "PIT", "Pittsburgh Pirates"
        SD = "SD", "San Diego Padres"
        SF = "SF", "San Francisco Giants"
        SEA = "SEA", "Seattle Mariners"
        STL = "STL", "St. Louis Cardinals"
        TB = "TB", "Tampa Bay Rays"
        TEX = "TEX", "Texas Rangers"
        TOR = "TOR", "Toronto Blue Jays"
        WSH = "WAS", "Washington Nationals"

    class NFL(models.TextChoices):
        NIL = None, "--------------------"
        ARI = "ARI", "Arizona Cardinals"
        ATL = "ATL", "Atlanta Falcons"
        BAL = "BAL", "Baltimore Ravens"
        BUF = "BUF", "Buffalo Bills"
        CAR = 'CAR', "Carolina Panthers"
        CHI = 'CHI', "Chicago Panthers"
        CIN = "CIN", "Cincinnati Bengals"
        CLE = "CLE", "Cleveland Browns"
        DAL = "DAL", "Dallas Cowboys"
        DEN = "DEN", "Denver Broncos"
        DET = "DET", "Detroit Lions"
        GB = "GB", "Green Bay Packers"
        HOU = "HOU", "Houston Texans"
        IND = "IND", "Indianapolis Colts"
        JAX = "JAX", "Jacksonville Jaguars"
        KC = "KC", "Kansas City Chiefs"
        MIA = "MIA", "Miami Dolphins"
        MIN = "MIN", "Minnesota Vikings"
        NE = "NE", "New England Patriots"
        NO = "NO", "New Orleans Saints"
        NYG = "NYG", "New York Giants"
        NYJ = "NYJ", "New York Jets"
        LV = "LV", "Las Vegas Raiders"
        PHI = "PHI", "Philadelphia Eagles"
        PIT = "PIT", "Pittsburgh Steelers"
        LAC = "LAC", "Los Angeles Chargers"
        SF = "SF", "San Francisco 49rs"
        SEA = "SEA", "Seattle Seahawks"
        LAR = "LAR", "Los Angeles Rams"
        TB = "TB", "Tampa Bay Buccaneers"
        TEN = "TEN", "Tennessee Titans"
        WAS = "WAS", "Washington Commanders"

    class NBA(models.TextChoices):
        NIL = None, "--------------------"
        ATL = "ATL", "Atlanta Hawks"
        BOS = "BOS", "Boston Celtics"
        CHA = "CHA", "Charlotte Hornets"
        CHI = "CHI", "Chicago Bulls"
        CLE = "CLE", "Cleveland Cavaliers"
        DAL = "DAL", "Dallas Mavericks"
        DEN = "DEN", "Denver Nuggets"
        DET = "DET", "Detroit Pistons"
        GSW = "GSW", "Golden State Warriors"
        HOU = "HOU", "Houston Rockets"
        IND = "IND", "Indiana Pacers"
        LAC = "LAC", "Los Angeles Clippers"
        LAL = "LAL", "Los Angeles Lakers"
        MEM = "MEM", "Memphis Grizzlies"
        MIA = "MIA", "Miami Heat"
        MIL = "MIL", "Milwaukee Bucks"
        MIN = "MIN", "Minnesota Timberwolves"
        NOH = "NOH", "New Orleans Pelicans"
        NYK = "NYK", "New York Knicks"
        BKN = "BKN", "Brooklyn Nets"
        OKC = "OKC", "Oklahoma City Thunder"
        ORL = "ORL", "Orlando Magic"
        PHI = "PHI", "Philadelphia 76ers"
        PHO = "PHO", "Phoenix Suns"
        POR = "POR", "Portland Trail Blazers"
        SAC = "SAC", "Sacramento Kings"
        TOR = "TOR", "Toronto Raptors"
        UTH = "UTH", "Utah Jazz"
        WAS = "WAS", "Washington Wizards"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)

    MALE = "M"
    FEMALE = "F"
    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), (None, "Prefer not to Say")]
    gender = models.CharField(choices=GENDER_CHOICES, default=None, null=True, blank=True, max_length=1)

    mlb = models.CharField(choices=MLB.choices, null=True, blank=True, default=None, max_length=20)
    nfl = models.CharField(choices=NFL.choices, null=True, blank=True, default=None, max_length=20)
    nhl = models.CharField(choices=NHL.choices, null=True, blank=True, default=None, max_length=20)
    nba = models.CharField(choices=NBA.choices, null=True, blank=True, default=None, max_length=20)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
