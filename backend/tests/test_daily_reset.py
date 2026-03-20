from backend.models import Product, StoreSettings
from backend.services.inventory import check_daily_reset
from datetime import datetime, timezone


def test_daily_reset_resets_tracked_stock(test_db):
    test_db.add(
        Product(
            id="fefefefe-fefe-fefe-fefe-fefefefefefe",
            name="Tracked",
            price=2,
            category_id=None,
            created_at="2026-03-20T00:00:00Z",
            stock=8,
            track_stock=True,
        )
    )
    test_db.add(
        StoreSettings(
            id=1,
            company_name="",
            last_stock_reset="Mon Mar 16 2026",
        )
    )
    test_db.commit()

    ran = check_daily_reset(test_db)
    test_db.commit()

    assert ran is True
    product = test_db.query(Product).filter(Product.id == "fefefefe-fefe-fefe-fefe-fefefefefefe").first()
    assert product.stock == 0


def test_daily_reset_skips_when_already_reset_today(test_db):
    today_js = datetime.now(timezone.utc).strftime("%a %b %d %Y")
    test_db.add(StoreSettings(id=1, company_name="", last_stock_reset=today_js))
    test_db.commit()

    ran = check_daily_reset(test_db)
    assert ran is False
