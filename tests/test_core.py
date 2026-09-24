from datetime import datetime,timezone
from trading_platform.core import OptionTrade,tags,repeated_activity,forward_study

def t(sec): return OptionTrade(datetime.fromtimestamp(sec,tz=timezone.utc),"ABC","2030-01-01",100,"call",2,1.99,2,200,100,source="test")

def test_tags():
    x=t(1); assert x.premium==40000; assert x.quote_side=="ask"; assert "large_premium" in tags(x); assert "size_gt_open_interest" in tags(x)

def test_repeat():
    e=repeated_activity([t(1),t(30),t(60)]); assert len(e)==1; assert e[0]["trade_count"]==3

def test_forward():
    x=t(100); x.underlying=100; points=[(x.ts,100),(datetime.fromtimestamp(200,tz=timezone.utc),101),(datetime.fromtimestamp(300,tz=timezone.utc),99)]
    r=forward_study([x],points,(100,))[0]; assert r["return_pct"]==0; assert r["max_favorable_pct"]==1; assert r["max_adverse_pct"]==-1
