from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import init_db, get_db
from models import Produit, Fournisseur, Chantier, ProduitFournisseur
from utils import PrixComparator, FournisseurComparator
from sqlalchemy.orm import Session
import json

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'

init_db()

@app.route('/')
def index():
    db = next(get_db())
    try:
        stats = {
            'produits': db.query(Produit).count(),
            'fournisseurs': db.query(Fournisseur).count(),
            'chantiers': db.query(Chantier).count(),
            'offres': db.query(ProduitFournisseur).count()
        }
        
        derniers_produits = db.query(Produit).order_by(Produit.id.desc()).limit(5).all()
        chantiers_actifs = db.query(Chantier).limit(5).all()
        
        return render_template('index.html', stats=stats, 
                             derniers_produits=derniers_produits,
                             chantiers_actifs=chantiers_actifs)
    finally:
        db.close()

@app.route('/produits')
def gerer_produits():
    db = next(get_db())
    try:
        produits = db.query(Produit).all()
        return render_template('produits.html', produits=produits)
    finally:
        db.close()

@app.route('/ajouter_produit', methods=['POST'])
def ajouter_produit():
    nom = request.form['nom']
    categorie = request.form['categorie']
    unite = request.form['unite']
    description = request.form['description']
    
    db = next(get_db())
    try:
        produit = Produit(nom=nom, categorie=categorie, unite=unite, description=description)
        db.add(produit)
        db.commit()
        flash('Produit ajouté avec succès!', 'success')
        return redirect(url_for('gerer_produits'))
    finally:
        db.close()

@app.route('/supprimer_produit', methods=['POST'])
def supprimer_produit():
    produit_id = request.form.get('id')
    
    if produit_id:
        db = next(get_db())
        try:
            produit = db.query(Produit).filter(Produit.id == produit_id).first()
            if produit:
                # Supprimer d'abord les offres associées
                db.query(ProduitFournisseur).filter(ProduitFournisseur.produit_id == produit_id).delete()
                # Puis supprimer le produit
                db.delete(produit)
                db.commit()
                flash('Produit supprimé avec succès!', 'success')
            else:
                flash('Produit non trouvé', 'error')
        except Exception as e:
            db.rollback()
            flash(f'Erreur lors de la suppression: {str(e)}', 'error')
        finally:
            db.close()
    else:
        flash('ID du produit manquant', 'error')
    
    return redirect(url_for('gerer_produits'))

@app.route('/fournisseurs')
def gerer_fournisseurs():
    db = next(get_db())
    try:
        fournisseurs = db.query(Fournisseur).all()
        return render_template('fournisseurs.html', fournisseurs=fournisseurs)
    finally:
        db.close()

@app.route('/ajouter_fournisseur', methods=['POST'])
def ajouter_fournisseur():
    nom = request.form['nom']
    adresse = request.form['adresse']
    telephone = request.form['telephone']
    email = request.form['email']
    
    db = next(get_db())
    try:
        fournisseur = Fournisseur(nom=nom, adresse=adresse, telephone=telephone, email=email)
        db.add(fournisseur)
        db.commit()
        flash('Fournisseur ajouté avec succès!', 'success')
        return redirect(url_for('gerer_fournisseurs'))
    finally:
        db.close()

@app.route('/chantiers')
def gerer_chantiers():
    db = next(get_db())
    try:
        chantiers = db.query(Chantier).all()
        return render_template('chantiers.html', chantiers=chantiers)
    finally:
        db.close()

@app.route('/ajouter_chantier', methods=['POST'])
def ajouter_chantier():
    nom = request.form['nom']
    adresse = request.form['adresse']
    date_debut = request.form['date_debut']
    date_fin = request.form['date_fin']
    
    db = next(get_db())
    try:
        chantier = Chantier(nom=nom, adresse=adresse, date_debut=date_debut, date_fin=date_fin)
        db.add(chantier)
        db.commit()
        flash('Chantier ajouté avec succès!', 'success')
        return redirect(url_for('gerer_chantiers'))
    finally:
        db.close()

@app.route('/comparaison')
def comparaison():
    db = next(get_db())
    try:
        produits = db.query(Produit).all()
        chantiers = db.query(Chantier).all()
        fournisseurs = db.query(Fournisseur).all()
        return render_template('comparaison.html', produits=produits, chantiers=chantiers, fournisseurs=fournisseurs)
    finally:
        db.close()

@app.route('/comparer_prix')
def comparer_prix():
    produit_id = request.args.get('produit_id')
    
    db = next(get_db())
    try:
        offres = PrixComparator.comparer_prix(int(produit_id), db)
        resultats = []
        
        for offre in offres:
            resultats.append({
                'fournisseur': offre.fournisseur.nom,
                'prix': offre.prix,
                'delai': offre.delai_livraison,
                'telephone': offre.fournisseur.telephone
            })
        
        return jsonify(resultats)
    finally:
        db.close()

@app.route('/trouver_fournisseur_proche')
def trouver_fournisseur_proche():
    chantier_id = request.args.get('chantier_id')
    produit_id = request.args.get('produit_id')
    
    db = next(get_db())
    try:
        comparator = FournisseurComparator()
        resultat = comparator.trouver_fournisseur_proche(int(chantier_id), int(produit_id), db)
        
        if resultat:
            offre, distance = resultat
            return jsonify({
                'fournisseur': offre.fournisseur.nom,
                'prix': offre.prix,
                'distance': round(distance, 2),
                'adresse': offre.fournisseur.adresse,
                'telephone': offre.fournisseur.telephone
            })
        
        return jsonify({'error': 'Aucun fournisseur trouvé'})
    finally:
        db.close()

@app.route('/ajouter_offre_prix', methods=['POST'])
def ajouter_offre_prix():
    produit_id = request.form['produit_id']
    fournisseur_id = request.form['fournisseur_id']
    prix = float(request.form['prix'])
    delai_livraison = int(request.form['delai_livraison'])
    
    db = next(get_db())
    try:
        offre = ProduitFournisseur(
            produit_id=produit_id,
            fournisseur_id=fournisseur_id,
            prix=prix,
            delai_livraison=delai_livraison
        )
        db.add(offre)
        db.commit()
        flash('Offre de prix ajoutée avec succès!', 'success')
        return redirect(url_for('comparaison'))
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

