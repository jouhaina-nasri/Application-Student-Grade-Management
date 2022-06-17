from flask import Flask, render_template,request,redirect,session,url_for,jsonify,flash
import mysql.connector 
import os
from passlib.hash import sha256_crypt


app=Flask(__name__)
#connecter avec la base #
conn=mysql.connector.connect(host="localhost",user="root",password="",database="gestionnotes")
mycursor = conn.cursor()
app.secret_key=os.urandom(24)
#----------------------------------#


#-------------------------------------------------------------------------------------------------------#
# gestion des utilisateur -- afficher -- #
@app.route('/manage_user')
def manage_user ():
    if'user_id' in session :
        mycursor.execute("""SELECT * FROM user where id<>'{}' and actif='1' """.format(session['user_id']))
        data=mycursor.fetchall()
        if session['Role']=='admin' :
           return render_template('user.html', prof = data, user=session['Role'])
        else :
           return render_template('contactuser.html', prof = data, user=session['Role'])
    else:
        return redirect('/login')
#################


# gestion des utilisateur -- afficher bloque-- #
@app.route('/bloque')
def bloque ():
    if'user_id' in session :
        mycursor.execute("""SELECT * FROM user where actif='0' """.format(session['user_id']))
        data=mycursor.fetchall()
        return render_template('bloque.html', prof = data, user=session['Role'])
    else:
        return redirect('/login')
#################


#gestion des utilisateur -- insert --#
@app.route('/insert', methods = ['POST'])
def insert():

    if request.method == "POST":
        id = request.form['id']   
        name = request.form['name']    
        email = request.form['email']
        motdepasse = request.form['motdepasse'] 
        password = sha256_crypt.encrypt((str(motdepasse)))
        Role=str((request.form['Role']))
        mycursor.execute("""SELECT * FROM user WHERE id ='{}' or email='{}' """.format(id,email))
        x=mycursor.fetchall()
        if len(x) > 0:
           flash("L'utilisateur existe déjà")
        else:
           mycursor.execute("INSERT INTO user (id,nom, email, motdepasse,Role) VALUES(%s, %s, %s, %s, %s)", (id, name, email, password, Role))
           conn.commit()
           if Role=='admin':
              mycursor.execute(""" INSERT INTO admin (ID_admin) VALUES ('{}') """.format(id))
              conn.commit()
           elif Role=='moniteur':
              mycursor.execute(""" INSERT INTO moniteur (id_moniteur) VALUES ('{}') """.format(id))
              conn.commit()
           elif Role=='prof':
              mycursor.execute(""" INSERT INTO prof (idprof) VALUES ('{}') """.format(id))
              conn.commit()
           else:
              mycursor.execute(""" INSERT INTO etudiant (idetudiant) VALUES ('{}') """.format(id))
              conn.commit()
           flash("Utilisateur est ajouté avec succès")
    return redirect('/manage_user')
##############



# gestion des utilisateurs -- modifier --#
@app.route('/update', methods = ['POST', 'GET'])
def update():

    if request.method == "POST": 
        id_data = request.form['id'] 
        name = request.form['name']    
        email = request.form['email']
        Role=str((request.form['Role']))  
        mycursor.execute("""SELECT * FROM user WHERE id='{}' """.format(id_data))
        data=mycursor.fetchall()
        if(email!=data[0][2]):
           mycursor.execute("""SELECT * FROM user WHERE email='{}' and id<>'{}' """.format(email,id_data))
           x=mycursor.fetchall()
           if len(x) > 0:
              flash("Les informations sont erronées ")
        else:
           mycursor.execute("""UPDATE user SET nom=%s, email=%s, Role=%s where id=%s """,(name, email, Role, id_data))
           flash("Utilisateur est modifier avec succès")
           conn.commit()
    return redirect('/manage_user')
#---------------------------#


#-------------------------#
#gestion des utilisateurs -- Block --#
@app.route('/block/<string:id_data>', methods = ['GET'])
def block(id_data):
        flash("Utilisateur est bloqué")
        mycursor.execute("""UPDATE user set actif='0' WHERE id=%s""", (id_data,))
        conn.commit()
        return redirect('/manage_user')
#-------------------------#


#-------------------------#
#gestion des utilisateurs -- unBlock --#
@app.route('/unblock/<string:id_data>', methods = ['GET'])
def unblock(id_data):
        flash("Utilisateur est débloqué")
        mycursor.execute("""UPDATE user set actif='1' WHERE id=%s""", (id_data,))
        conn.commit()
        return redirect('/bloque')
#-------------------------#


#-------------------------------------------------------------------------------------------------------#






#-------------------------------------------------------------------------------------------------------#
# gestion des modules -- afficher -- #
@app.route('/module')
def module ():
    if'user_id' in session :
        mycursor.execute("SELECT * FROM module")
        data=mycursor.fetchall()
        if session['Role']=='admin' or session['Role']=='moniteur' :
           return render_template('module.html', module = data, user=session['Role'])
        else :
           return render_template('affichemodule.html', module = data, user=session['Role'])
    else:
        return redirect('/login')
#####################


#gestion des modules -- insert -- #
@app.route('/insertm', methods = ['POST'])
def insertm():
    if request.method == "POST":
        refmodule = request.form['refmodule']      
        nom_module = request.form['nom_module'] 
        coeff= request.form['coeff']
        mycursor.execute("""SELECT * FROM module WHERE refmodule ='{}' or nom_module='{}' """.format(refmodule,nom_module))
        x=mycursor.fetchall()
        if len(x) > 0:
           flash("Les informations sont erronées")
        else:
            flash("Module est ajouté avec succès")
            mycursor.execute("INSERT INTO module (refmodule, nom_module,coefficient) VALUES(%s, %s, %s)", (refmodule, nom_module,coeff))
            conn.commit()
    return redirect('/module')
#------------------------# 


#gestion des modules -- modifier --#
@app.route('/updatem', methods = ['POST', 'GET'])
def updatem():

    if request.method == "POST":
        refmodule = request.form['refmodule']     
        nom_module = request.form['nom_module']
        coeff= request.form['coeff']
        mycursor.execute("""SELECT * FROM module WHERE refmodule='{}' """.format(refmodule))
        data=mycursor.fetchall()
        if(nom_module!=data[0][1]):
           mycursor.execute("""SELECT * FROM module WHERE nom_module='{}' and refmodule<>'{}' """.format(nom_module,refmodule))
           x=mycursor.fetchall()
           if len(x) > 0:
              flash("Les informations sont erronées")
        else:
            mycursor.execute("""UPDATE module SET nom_module=%s, coefficient=%s where refmodule=%s """, (nom_module, coeff, refmodule))
            flash("Module est modifié avec succès")
            conn.commit()
    return redirect('/module')

#--------------------------------#


#gestion des modules -- delete --#
@app.route('/deletem/<string:id_data>', methods = ['GET'])
def deletem(id_data):
        flash("Suppression avec succès")
        mycursor.execute("DELETE FROM module WHERE refmodule=%s", (id_data,))
        mycursor.execute("DELETE FROM matiere WHERE refmodule=%s", (id_data,))
        conn.commit()
        return redirect('/module')
#------------------------#

#-------------------------------------------------------------------------------------------------------#




#-------------------------------------------------------------------------------------------------------#
# gestion des matieres -- afficher -- #
@app.route('/matiere')
def matiere ():
    if'user_id' in session :
        mycursor.execute("SELECT * FROM matiere")
        data=mycursor.fetchall()
        if session['Role']=='admin' or session['Role']=='moniteur' :
           return render_template('matiere.html', matiere = data,user=session['Role'])
        else : 
           return render_template('affichematiere.html', matiere = data, user=session['Role'])
    else:
        return redirect('/login')
#######################


#gestion des matierers -- insert -- #
@app.route('/insertmat', methods = ['POST'])
def insertmat():

    if request.method == "POST":
        refmatiere = request.form['refmatiere']   
        refmodule = request.form['refmodule'] 
        nom_matiere = request.form['nom_matiere']    
        coefficient = request.form['coefficient'] 
        mycursor.execute("""SELECT * FROM matiere WHERE refmatiere ='{}' or nom_matiere='{}' """.format(refmatiere,nom_matiere))
        x=mycursor.fetchall()
        if len(x) > 0:
           flash("Les informations sont erronées")
        else:
           mycursor.execute("""SELECT * FROM module WHERE refmodule ='{}' """.format(refmodule))
           data=mycursor.fetchall()
           if(len(data)>0):
              flash("Matière est ajouté avec succès")  
              mycursor.execute("INSERT INTO matiere (refmatiere,refmodule,nom_matiere,coefficient) VALUES(%s, %s, %s, %s)", (refmatiere,refmodule,nom_matiere,coefficient))
              conn.commit()
           else:
              flash("le module n'existe pas")	
    return redirect('/matiere')
#----------------------------#

#gestion des matieres -- modifier --#
@app.route('/updatemat', methods = ['POST', 'GET'])
def updatemat():

    if request.method == "POST":
        refmatiere = request.form['refmatiere']   
        refmodule = request.form['refmodule']
        nom_matiere = request.form['nom_matiere']  
        coefficient = request.form['coefficient'] 
        mycursor.execute("""SELECT * FROM matiere WHERE refmatiere='{}' """.format(refmatiere))
        data=mycursor.fetchall()
        if(nom_matiere!=data[0][2]):
           mycursor.execute("""SELECT * FROM matiere WHERE nom_matiere='{}' and refmatiere<>'{}' """.format(nom_matiere,refmatiere))
           x=mycursor.fetchall()
           if len(x) > 0:
              flash("les informations sont erronées")
           else:
              mycursor.execute("""UPDATE matiere SET nom_matiere=%s,coefficient=%s where refmatiere=%s """,(nom_matiere,coefficient,refmatiere))
              flash("Modification avec succès")
        else:
            mycursor.execute("""UPDATE matiere SET coefficient=%s where refmatiere=%s """,(coefficient, refmatiere))
            flash("Modification avec succès")
            conn.commit()
    return redirect('/matiere')

#-----------------------------#

#gestion des matieres -- delete --#
@app.route('/deletemat/<string:id_data>', methods = ['GET'])
def deletemat(id_data):
        flash("Suppression avec succès")
        mycursor.execute("DELETE FROM matiere WHERE refmatiere=%s", (id_data,))
        conn.commit()
        return redirect('/matiere')
#----------------------------#
#-------------------------------------------------------------------------------------------------------#





#-------------------------------------------------------------------------------------------------------#
#gestion des etudiant -- afficher--#
@app.route('/etudiant')
def etudiant ():
    if'user_id' in session :
        mycursor.execute("SELECT * FROM affectation where id_etudiant in (SELECT id FROM user WHERE Role='etudiant' AND actif='1')")
        data=mycursor.fetchall()
        return render_template('etudiant.html', etudiant = data, user=session['Role'])
    else:
       return redirect('/login')
#--------------#


#gestion des etudiants -- insert --#
@app.route('/insertetud', methods = ['POST'])
def insertetud():

    if request.method == "POST":
        id = request.form['id']   
        refclasse = request.form['refclasse'] 
        niveau = request.form['niveau'] 
        mycursor.execute("""SELECT * FROM affectation WHERE id_etudiant ='{}' and id_classe ='{}' """.format(id,refclasse))
        x=mycursor.fetchall()
        if len(x)>0 :
           flash("les informations sont erronées")
        else:
            mycursor.execute("""SELECT * FROM user WHERE id ='{}' and actif='1' and Role='etudiant' """.format(id))
            a=mycursor.fetchall()
            if len(a)>0:
                mycursor.execute("INSERT INTO affectation (id_etudiant,id_classe,niveau) VALUES(%s,%s, %s)", (id,refclasse,niveau))
                conn.commit()
                flash("Ajout avec succès")
            else:
                flash("Etudiant n'existe pas")
    return redirect('/etudiant')
#--------------------------#



#gestion des etudiants -- modifier --#
@app.route('/updateetud', methods = ['POST', 'GET'])
def updateetud():

    if request.method == "POST":
        id = request.form['id']   
        refclasse = request.form['refclasse'] 
        niveau = request.form['niveau'] 
        mycursor.execute(""" UPDATE affectation SET id_classe=%s, niveau=%s where id_etudiant=%s """,(refclasse,niveau,id))
        flash("Modification avec succès")
        conn.commit()
    return redirect('/etudiant')
#----------------------------------#



#gestion des etudiants -- delete --#
@app.route('/deleteetud/<string:id_data>', methods = ['GET'])
def deleteetud(id_data):
        flash("Suppression avec succès")
        mycursor.execute("DELETE FROM affectation WHERE id_etudiant=%s", (id_data,))
        conn.commit()
        return redirect('/etudiant')
#--------------------------------------------#
#-------------------------------------------------------------------------------------------------------#




#-------------------------------------------------------------------------------------------------------#
#gestion des notes -- afficher --#
@app.route('/note')
def note ():
    if'user_id' in session :
        if session['Role']!='etudiant' :
           mycursor.execute("SELECT * FROM note")
           data=mycursor.fetchall()
           if session['Role']=='prof' :
              return render_template('note.html', note = data,user=session['Role'])
           else :
              return render_template('affichenote.html', note = data,user=session['Role'])
        else:
            mycursor.execute("SELECT * FROM note where idetudiant='{}'".format(session['user_id']))
            data=mycursor.fetchall()
            return render_template('affichenote.html', note = data,user=session['Role'])
    else:
       return redirect('/login')


#gestion des notes -- insert -- #
@app.route('/insertn', methods = ['POST'])
def insertn():

    if request.method == "POST":
        idnote = request.form['idnote'] 
        idetudiant = request.form['idetudiant']   
        refmatiere = request.form['refmatiere']    
        note = request.form['note'] 
        mycursor.execute("""SELECT * FROM note WHERE idnote ='{}'  """.format(idnote))
        x=mycursor.fetchall()
        if len(x)>0 :
            flash("Les informations sont erronées")
        else:
            mycursor.execute("""SELECT * FROM etudiant WHERE idetudiant ='{}'  """.format(idetudiant))
            a=mycursor.fetchall()
            if len(a)>0 :
                mycursor.execute("""SELECT * FROM matiere WHERE refmatiere ='{}'  """.format(refmatiere))
                b=mycursor.fetchall()	
                if len(b)>0 :
                   mycursor.execute("INSERT INTO note (idnote,idetudiant,refmatiere, note, idprof) VALUES(%s,%s, %s, %s, %s)", (idnote, idetudiant,refmatiere, note, session['user_id']))
                   conn.commit()
                   flash("Ajout avec succès")
                else:
                   flash("Matiere n'existe pas")
            else:
                flash("Etudiant n'existe pas")
    return redirect('/note')
#----------------------------------#



#gestion des notes -- modifier-- #
@app.route('/updaten', methods = ['POST', 'GET'])
def updaten():

    if request.method == "POST":
        idnote = request.form['idnote']  
        idetudiant = request.form['idetudiant']   
        refmatiere = request.form['refmatiere']    
        note = request.form['note'] 
        mycursor.execute("""SELECT * FROM user WHERE id ='{}' and actif='1' and Role="etudiant"  """.format(idetudiant))
        a=mycursor.fetchall()
        if len(a)>0 :
            mycursor.execute("""SELECT * FROM matiere WHERE refmatiere ='{}'  """.format(refmatiere))
            b=mycursor.fetchall()	
            if len(b)>0 :
                mycursor.execute("""UPDATE note SET note=%s, idetudiant=%s, refmatiere=%s where idnote=%s""",(note, idetudiant, refmatiere, idnote))
                flash("Modification avec succès")
                conn.commit()
            else:
                flash("Matiere n'existe pas")
        else:
            flash("Etudiant n'existe pas")
    return redirect('/note')
#------------------------------------------#



#gestion des notes -- delete -- #
@app.route('/deleten/<string:id_data>', methods = ['GET'])
def deleten(id_data):
        flash("Suppression avec succès")
        mycursor.execute("DELETE FROM note WHERE idetudiant=%s", (id_data,))
        conn.commit()
        return redirect('/note')
#----------------------------------#

#-------------------------------------------------------------------------------------------------------#

#-------------------------------------------------------------------------------------------------------#
#gestion des resultat -- calculer moyenne --#
@app.route('/calcul',methods = ['POST'])
def calcul ():
    if'user_id' in session :
        idetudiant = request.form['id']  
        mycursor.execute("SELECT * from note where idetudiant='{}' ".format(idetudiant))
        ch=mycursor.fetchall()
        if len(ch)>0:   
            mycursor.execute("SELECT * from bulltin where id_etudiant='{}' ".format(idetudiant))
            x=mycursor.fetchall()
            if len(x)>0:
                flash("Etudiant déja a un moyenne")
            else:
                mycursor.execute("INSERT INTO bulltin SELECT note.idetudiant,module.nom_module,module.coefficient,SUM(note.note*matiere.coefficient)/SUM(matiere.coefficient) FROM matiere,note,module WHERE note.idetudiant='{}' AND note.refmatiere=matiere.refmatiere AND matiere.refmodule=module.refmodule  GROUP BY module.refmodule".format(idetudiant))
                conn.commit()
                mycursor.execute("INSERT INTO resultat SELECT bulltin.id_etudiant,SUM(bulltin.moyenne*bulltin.coefficient)/SUM(bulltin.coefficient) FROM bulltin WHERE bulltin.id_etudiant='{}'".format(idetudiant))
                conn.commit()
                flash("sucess")
        else:
            flash("Etudiant n'a pas une note") 
        return redirect('note')
    else:
       return redirect('/login')
#-----------------------------------#
#-------------------------------------------------------------------------------------------------------#



#-------------------------------------------------------------------------------------------------------#
#gestion des resultat -- afficher --#
@app.route('/resultat')
def resultat ():
    if'user_id' in session :
        if session['Role']=='etudiant':
            mycursor.execute("SELECT * from bulltin where id_etudiant='{}' ".format(session['user_id']))
            ch=mycursor.fetchall()
            total=""
            moyenne=""
            if len(ch)>0:           
              mycursor.execute("SELECT SUM(bulltin.moyenne)FROM bulltin WHERE bulltin.id_etudiant='{}'".format(session['user_id']))
              total=mycursor.fetchall()
              mycursor.execute("SELECT resultat.moyenne FROM resultat WHERE resultat.idetudiant='{}'".format(session['user_id']))
              moyenne=mycursor.fetchall()
              return render_template('bulltin.html', resultat = ch,moyenne = moyenne,total=total, user=session['Role'])
            else:
              return render_template('bulltin.html', resultat = ch,moyenne = moyenne,total=total, user=session['Role'])
        else:
            mycursor.execute("SELECT * from  resultat")
            data=mycursor.fetchall()
            return render_template('resultat.html', resultat = data,user=session['Role'])
    else:
        return redirect('/login')
#-----------------------------------#
#gestion des resultat -- delete --#
@app.route('/deleteresult/<string:id_data>', methods = ['GET'])
def deleteresult(id_data):
        flash("Suppression avec succès")
        mycursor.execute("DELETE FROM resultat WHERE idetudiant=%s", (id_data,))
        conn.commit()
        return redirect('/resultat')
#-----------------------------------#
#-------------------------------------------------------------------------------------------------------#






#-------------------------------------------------------------------------------------------------------#
# page d'accueil #
@app.route('/')
def accueil ():
    return render_template('index.html')
###########

# login #
@app.route('/login')
def login ():
    return render_template('login.html')
##############
#page inscription #
@app.route('/register')
def about ():
    return render_template('register.html')
#------------------------#


#page profil #
@app.route('/profile')
def home ():
    return render_template('profile.html',user=session['Role'])
#----------------------------#


#validation de login existe ou non#
@app.route('/login_validation', methods=['POST'])
def login_validation ():

    email=request.form.get('email')
    motdepasse=request.form.get('password')
    mycursor.execute(""" SELECT * from user where email='{}'""".format(email))
    session.pop('user',None)
    users=mycursor.fetchall()
    data = users[0][3]
    if sha256_crypt.verify(motdepasse, data):
        if (users[0][5]==1):
            session['user_id']=users[0][0]
            session['user']=users[0][1]
            session['Role']=users[0][4]
            return render_template('profile.html',user=session['Role'])
        else:
            return redirect('/login')
    else:
        return redirect('/login')
#--------------------------------#


#inscription -- ajouter --#
@app.route('/add_user',methods=['POST'])
def add_user ():
    id=request.form.get('id')
    name=request.form.get('uname')
    email=request.form.get('uemail')
    motdepasse=request.form.get('upassword')
    password = sha256_crypt.encrypt((str(motdepasse)))
    Role=str((request.form['Role']))
    mycursor.execute("""SELECT * FROM user WHERE id ='{}' or email='{}' """.format(id,email))
    x=mycursor.fetchall()
    if len(x) > 0:
       flash("Exist")
       return render_template('register.html')
    else:
       mycursor.execute(""" INSERT INTO user (id,nom,email,motdepasse,Role) VALUES ('{}','{}','{}','{}','{}') """.format(id,name,email,password,Role))
       conn.commit()
       if Role=='admin':
          mycursor.execute(""" INSERT INTO admin (ID_admin) VALUES ('{}') """.format(id))
          conn.commit()
       elif Role=='moniteur':
          mycursor.execute(""" INSERT INTO moniteur (id_moniteur) VALUES ('{}') """.format(id))
          conn.commit()
       elif Role=='prof':
          mycursor.execute(""" INSERT INTO prof (idprof) VALUES ('{}') """.format(id))
          conn.commit()
       else :
          mycursor.execute(""" INSERT INTO etudiant (idetudiant) VALUES ('{}') """.format(id))
          conn.commit()
       mycursor.execute("""SELECT * FROM user WHERE email LIKE '{}' and id='{}' """.format(email,id))
       myuser=mycursor.fetchall()
       session['user_id']=myuser[0][0]
       return redirect('/login')
#---------------------------------#


#deconnecte#
@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')
#-----------------------------#

#-------------------------------------------------------------------------------------------------------#


#main#
if __name__=="__main__":
    app.run(debug=True)
#------------------------#

#page d'erreur#
@app.errorhandler(500)
def invalide_route(e):
    return render_template('404.html')
    return jsonify({'errorCode':500,'message':'Route not found'})
#------------------------#