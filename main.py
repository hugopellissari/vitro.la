from flask import Flask, render_template, request, jsonify, redirect, flash
from wtforms import StringField, SubmitField
from flask_wtf import Form
from wtforms.validators import DataRequired, Regexp
import sqlite3 as sql
import collections


app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisismyfuckingsecretkey'
app.config['CSRF_ENABLED'] = True

dbPath="C:\\Users\\K45VM-VX105H\Desktop\\jk-trying to save\\aqueous-ravine-18064\\jukebox.db"

class createForm(Form):
    jukeName = StringField('jukeName', validators=[DataRequired(message="You have to name your jukebox"), Regexp('^[a-zA-Z]*$',message="Only letters are allowed, no space allowed")])
    createButton = SubmitField()

class remoteForm(Form):
    jukeName2 = StringField('jukeName', validators=[DataRequired(message="You have to name your jukebox"), Regexp('^[a-zA-Z]*$',message="Only letters are allowed, no space allowed")])
    remoteButton = SubmitField()

def create_juketable(tablename):
    con = sql.connect(dbPath)
    cur = con.cursor()
    configTable = tablename+'_config'
    try:
        cur.execute("CREATE TABLE %s (id integer primary key autoincrement, videoid text not null, title text not null, duration text not null, pos integer not null)" % tablename)
        cur.execute("CREATE TABLE %s (id integer primary key autoincrement, authFlag integer, playcursor integer)" % configTable)
        query = "INSERT INTO {0} (authFlag, playcursor) VALUES(1,0)".format(configTable)
        cur.execute(query)
        con.commit()
    except:
        return False
    con.close()


def add_video(tablename, videoURL, videoTitle, videoDuration, vlocation, vcursor):
    con = sql.connect(dbPath)
    cur = con.cursor()
    location = int(vlocation)
    cursor = int(vcursor)
    if location == 0:
        query = "INSERT INTO {0} (videoid, title, duration,pos) VALUES(?,?,?,(SELECT COUNT(*) FROM {1})+1)".format(tablename, tablename)
        cur.execute(query, (videoURL, videoTitle, videoDuration))
    else:
        cur.execute("UPDATE {0} SET pos=pos+1 WHERE pos>{1}".format(tablename, cursor + 1))
        query = "INSERT INTO {0} (videoid, title, duration,pos) VALUES(?,?,?,?)".format(tablename, tablename)
        cur.execute(query, (videoURL, videoTitle, videoDuration,cursor+2))
    con.commit()
    con.close()

#Recupera playlist da database, transforma em JSON
def get_playlist(tablename):
    con = sql.connect(dbPath)
    cur = con.cursor()
    cur.execute("SELECT * FROM %s ORDER BY pos" % tablename)
    rows = cur.fetchall()
    con.commit()
    con.close()

    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['videoid'] = row[1]
        d['title'] = row[2]
        d['duration'] = row[3]
        d['pos'] = row[4]
        objects_list.append(d)

    return jsonify(objects_list)

def get_cursor(tablename):
    con = sql.connect(dbPath)
    cur = con.cursor()
    cur.execute("SELECT authFlag, playcursor FROM %s WHERE id=1" % tablename)
    rows = cur.fetchall()
    con.commit()
    con.close()

    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['authFlag'] = row[0]
        d['playcursor'] = row[1]
        objects_list.append(d)

    return jsonify(objects_list)

def update_cursor(tablename,vcursor):
    con = sql.connect(dbPath)
    cur = con.cursor()
    cursor = int(vcursor)
    query = "UPDATE {0} SET playcursor={1} WHERE id=1".format(tablename,cursor)
    cur.execute(query)
    con.commit()
    con.close()


#Reordena playlist, parametro "direction" indica se vai para cima ou para baixo sendo 0=desce 1=sobe
def reorder_playlist(tablename, id, dir):
    con = sql.connect(dbPath)
    cur = con.cursor()
    cur.execute("SELECT pos FROM {0} WHERE id={1}".format(tablename,int(id)))
    position = int(cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM {0}".format(tablename))
    maxPosition = int(cur.fetchone()[0])
    direction = int(dir)
    if direction == 0 and position > 1:
        print("entred 0")
        query = "UPDATE {0} SET pos=pos+1 WHERE pos=(SELECT pos-1 FROM {1} WHERE id={2})".format(tablename, tablename, int(id))
        cur.execute(query)
        query = "UPDATE {0} SET pos=pos-1  WHERE id={1}".format(tablename, int(id))
        cur.execute(query)
    elif direction == 1 and position < maxPosition:
        print("entred 1")
        query = "UPDATE {0} SET pos=pos-1 WHERE pos=(SELECT pos+1 FROM {1} WHERE id={2})".format(tablename, tablename, int(id))
        cur.execute(query)
        query = "UPDATE {0} SET pos=pos+1  WHERE id={1}".format(tablename, int(id))
        cur.execute(query)
    con.commit()
    con.close()

def clear(tablename, id):
    con = sql.connect(dbPath)
    cur = con.cursor()

    cur.execute("SELECT pos FROM {0} WHERE id={1}".format(tablename,int(id)))
    position = int(cur.fetchone()[0])

    cur.execute("DELETE FROM {0} WHERE id={1}".format(tablename, int(id)))
    cur.execute("UPDATE {0} SET pos=pos-1 WHERE pos>{1}".format(tablename, position))
    con.commit()
    con.close()

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"%s" % (
                error
            ))


@app.route('/', methods=['GET', 'POST'])
def index():
    #Ativa o player caso esteja tudo certo
    formCreatePlaylist = createForm()
    formRemote=remoteForm()

    if formCreatePlaylist.createButton.data and formCreatePlaylist.validate_on_submit():
        #se validado corretamente, adiciona na db e renderiza pagina
        jukename = request.form["jukeName"].lower()
        if(create_juketable(jukename)==False):
            flash("This table already exists")
            return render_template("index.html", formCreatePlaylist=formCreatePlaylist, formRemote=formRemote)
        else:
            return render_template("player.html", jukename=jukename)

    if formRemote.remoteButton.data and formRemote.validate_on_submit():
        jukename = request.form["jukeName2"].lower()
        if(create_juketable(jukename)!=False):
            flash("We couldn't find this jukebox. Maybe you should create one")
            return render_template("index.html", formCreatePlaylist=formCreatePlaylist, formRemote=formRemote)
        else:
            return render_template("remote.html", jukename=jukename)


    flash_errors(formCreatePlaylist)
    return render_template("index.html", formCreatePlaylist=formCreatePlaylist, formRemote=formRemote)

@app.route('/getCursor', methods=['GET', 'POST'])
def getCursor():
     tablename = request.form["jukename"]+'_config'
     return get_cursor(tablename)

@app.route('/updateCursor', methods=['GET', 'POST'])
def updateCursor():
    tablename = request.form["jukename"]+'_config'
    vcursor = request.form["cursor"]
    update_cursor(tablename, vcursor)
    return jsonify(result={"status": 200})

@app.route('/add', methods=['POST'])
def add():
    tablename = request.form["jukename"]
    videoURL = request.form["url"]
    videoTitle = request.form["videoTitle"]
    videoDuration = request.form["videoDuration"]
    vlocation = request.form["location"]
    vcursor = request.form["cursor"]

    add_video(tablename, videoURL, videoTitle, videoDuration, vlocation, vcursor)
    return jsonify(result={"status": 200})


@app.route('/showPlaylist', methods=['POST'])
def showPlaylist():
    tablename = request.form["jukename"]
    return get_playlist(tablename)

@app.route('/reorder', methods=['POST'])
def reorder():
    tablename = request.form["jukename"]
    id = request.form["id"]
    direction = request.form["direction"]
    reorder_playlist(tablename, id, direction)
    return jsonify(result={"status": 200})

@app.route('/delete',methods=['POST'])
def delete():
    tablename = request.form["jukename"]
    id = request.form["id"]
    clear(tablename,id)
    return jsonify(result={"status": 200})


if __name__ == '__main__':
    app.run()
