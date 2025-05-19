from order_logic import create_new_order, get_orders

def test_create_new_order_mock(monkeypatch):
    class DummyConn:
        def cursor(self): return self
        def callproc(self, *_): pass
        def commit(self): pass
        def close(self): pass
        def __enter__(self): return self
        def __exit__(self, *_): pass

    monkeypatch.setattr('order_logic.get_connection', lambda: DummyConn())

    result = create_new_order(1, "Cash", 2, 5, "Test custom")
    assert result["success"] is True
    assert "berhasil" in result["message"]
