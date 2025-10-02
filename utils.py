from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import requests

class DistanceCalculator:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="gestion_chantier")
    
    def get_coordinates(self, adresse):
        try:
            location = self.geolocator.geocode(adresse + ", Côte d'Ivoire")
            if location:
                return location.latitude, location.longitude
        except:
            pass
        return None, None
    
    def calculate_distance(self, coord1, coord2):
        if coord1[0] and coord2[0]:
            return geodesic(coord1, coord2).kilometers
        return float('inf')

class PrixComparator:
    @staticmethod
    def comparer_prix(produit_id, db):
        from models import ProduitFournisseur
        
        offres = db.query(ProduitFournisseur).filter(
            ProduitFournisseur.produit_id == produit_id
        ).all()
        
        offres_triees = sorted(offres, key=lambda x: x.prix)
        return offres_triees
    
    @staticmethod
    def trouver_meilleur_prix(produit_id, db):
        offres = PrixComparator.comparer_prix(produit_id, db)
        return offres[0] if offres else None

class FournisseurComparator:
    def __init__(self):
        self.distance_calc = DistanceCalculator()
    
    def trouver_fournisseur_proche(self, chantier_id, produit_id, db):
        from models import Chantier, ProduitFournisseur
        
        chantier = db.query(Chantier).filter(Chantier.id == chantier_id).first()
        if not chantier or not chantier.latitude:
            return None
        
        offres = db.query(ProduitFournisseur).filter(
            ProduitFournisseur.produit_id == produit_id
        ).all()
        
        if not offres:
            return None
        
        fournisseurs_avec_distance = []
        for offre in offres:
            if offre.fournisseur.latitude:
                distance = self.distance_calc.calculate_distance(
                    (chantier.latitude, chantier.longitude),
                    (offre.fournisseur.latitude, offre.fournisseur.longitude)
                )
                fournisseurs_avec_distance.append((offre, distance))
        
        if fournisseurs_avec_distance:
            fournisseurs_avec_distance.sort(key=lambda x: x[1])
            return fournisseurs_avec_distance[0]
        
        return None