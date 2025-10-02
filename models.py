from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base  



class Fournisseur(Base):
    __tablename__ = 'fournisseurs'
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    adresse = Column(Text, nullable=False)
    telephone = Column(String(20))
    email = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    
    produits = relationship("ProduitFournisseur", back_populates="fournisseur")

class Chantier(Base):
    __tablename__ = 'chantiers'
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    adresse = Column(Text, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    date_debut = Column(String(50))
    date_fin = Column(String(50))
    
    @property
    def est_actif(self):
        from datetime import datetime
        if not self.date_fin:
            return True
        try:
            date_fin = datetime.strptime(self.date_fin, '%Y-%m-%d')
            return datetime.now() < date_fin
        except:
            return True

class Produit(Base):
    __tablename__ = 'produits'
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    description = Column(Text)
    categorie = Column(String(50))
    unite = Column(String(20))

class ProduitFournisseur(Base):
    __tablename__ = 'produit_fournisseur'
    
    id = Column(Integer, primary_key=True, index=True)
    produit_id = Column(Integer, ForeignKey('produits.id'))
    fournisseur_id = Column(Integer, ForeignKey('fournisseurs.id'))
    prix = Column(Float, nullable=False)
    delai_livraison = Column(Integer)
    
    produit = relationship("Produit")
    fournisseur = relationship("Fournisseur", back_populates="produits")

    