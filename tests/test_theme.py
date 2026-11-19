from app.theme import PALETTE, stylesheet

def test_application_palette_has_exactly_eight_colors():
    assert len(PALETTE) == 8
    assert set(PALETTE) == {"primary","secondary","accent","background","surface","surface_alt","text","muted"}
    assert all(value.startswith("#") and len(value)==7 for value in PALETTE.values())

def test_shared_stylesheet_uses_palette_roles():
    css=stylesheet()
    for value in PALETTE.values():
        assert value in css
