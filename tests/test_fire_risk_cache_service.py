from app.services.fire_risk_cache_service import FireRiskCacheService


class FakeSnapshot:
	def __init__(self, data):
		self._data = data

	@property
	def exists(self):
		return self._data is not None

	def to_dict(self):
		return self._data


class FakeDocumentReference:
	def __init__(self, store, document_id):
		self._store = store
		self._document_id = document_id

	def get(self):
		return FakeSnapshot(self._store.get(self._document_id))

	def set(self, data):
		self._store[self._document_id] = data


class FakeCollectionReference:
	def __init__(self, store):
		self._store = store

	def document(self, document_id):
		return FakeDocumentReference(self._store, document_id)


class FakeFirestoreClient:
	def __init__(self):
		self.store = {}

	def collection(self, _collection_name):
		return FakeCollectionReference(self.store)


def _build_service(monkeypatch, fake_client, fake_time):
	monkeypatch.setattr("app.services.fire_risk_cache_service.firestore.client", lambda: fake_client)
	monkeypatch.setattr("app.services.fire_risk_cache_service.time.time", lambda: fake_time)
	return FireRiskCacheService()


def test_get_grid_id_rounds_coordinates_and_uses_hour_slot(monkeypatch):
	service = _build_service(monkeypatch, FakeFirestoreClient(), fake_time=3661)

	grid_id = service.get_grid_id(lat=60.3913, lon=5.3221, points=12)

	assert grid_id == "grid_60.400_5.320_p12_t3600"


def test_get_cached_risk_returns_none_on_cache_miss(monkeypatch):
	service = _build_service(monkeypatch, FakeFirestoreClient(), fake_time=7200)

	cached = service.get_cached_risk(lat=60.3913, lon=5.3221, points=12)

	assert cached is None


def test_get_cached_risk_returns_result_on_cache_hit(monkeypatch):
	fake_client = FakeFirestoreClient()
	service = _build_service(monkeypatch, fake_client, fake_time=7200)

	grid_id = service.get_grid_id(lat=60.3913, lon=5.3221, points=12)
	expected_result = {"ttf": [12.5], "result": {"source": "cache"}}
	fake_client.store[grid_id] = {"result": expected_result}

	cached = service.get_cached_risk(lat=60.3913, lon=5.3221, points=12)

	assert cached == expected_result


def test_save_to_cache_persists_expected_payload(monkeypatch):
	fake_client = FakeFirestoreClient()
	service = _build_service(monkeypatch, fake_client, fake_time=9999)

	result_payload = {"ttf": [9.1], "result": {"risk": "low"}}
	service.save_to_cache(lat=60.3913, lon=5.3221, points=2, result=result_payload)

	grid_id = service.get_grid_id(lat=60.3913, lon=5.3221, points=2)
	stored = fake_client.store[grid_id]

	assert stored["grid_id"] == grid_id
	assert stored["points"] == 2
	assert stored["timestamp"] == 9999
	assert stored["result"] == result_payload
	assert stored["location"] == {"lat": 60.3913, "lon": 5.3221}
