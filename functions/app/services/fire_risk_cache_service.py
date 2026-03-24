from firebase_admin import firestore
import time

class FireRiskCacheService:
    def __init__(self):
        self.db = firestore.client()
        self.grid_res = 0.02 
        self.collection_name = "fire_risk_cache"

    def get_grid_id(self, lat, lon, points):
    
        slat = round(lat / self.grid_res) * self.grid_res
        slon = round(lon / self.grid_res) * self.grid_res
        
        timeslot = int(time.time() // 3600) * 3600
        
        return f"grid_{slat:.3f}_{slon:.3f}_p{points}_t{timeslot}"

    def get_cached_risk(self, lat, lon, points):
        grid_id = self.get_grid_id(lat, lon, points)
        doc_ref = self.db.collection(self.collection_name).document(grid_id)
        doc = doc_ref.get()

        if doc.exists:
            print(f"cache-treff for slot: {grid_id}")
            return doc.to_dict().get('result')
        
        return None

    def save_to_cache(self, lat, lon, points, result):
        grid_id = self.get_grid_id(lat, lon, points)
        doc_ref = self.db.collection(self.collection_name).document(grid_id)
        
        
        doc_ref.set({
            'grid_id': grid_id,
            'points': points,
            'timestamp': time.time(),
            'result': result, # Dette lagrer "ttf" og "result" 
            'location': {'lat': lat, 'lon': lon}
        })