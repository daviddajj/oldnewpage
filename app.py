import json
import os
import time
import cv2
import numpy as np
from flask import Flask, redirect,render_template,request, session, url_for

# UPLOAD_FOLDER = 'C:\oldnew\templates'
# ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.secret_key= b'oldnew'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB



# def allowed_file(filename):
#     return '.' in filename and \
# filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('oldnewpage/',methods=['POST','GET'])
def index():
	if request.method =='POST':
		if request.values['send']=='送出':
			return render_template('index.html',name=request.values['user'])
	return render_template('index.html',name="")

@app.route('oldnewpage/menu',methods=['GET','POST'])
def menu():
    return render_template('menu.html', template_folder='./')


@app.route('oldnewpage/register',methods=['POST','GET'])
def register():

	with open('oldnewpage/member.json','r') as file_object:
		member = json.load(file_object)
	if request.method=='POST':
		if request.values['send']=='送出':
			if request.values['userid'] in member:
				for find in member:
					if member[find]['nick']==request.values['username']:
						return render_template('register.html',alert='this account and nickname are used.')
				return render_template('register.html',alert='this account is used.',nick=request.values['username'])
			else:
				for find in member:
					if member[find]['nick']==request.values['username']:
						return render_template('register.html',alert='this nickname are used.',id=request.values['userid'],pw=request.values['userpw'])
				member[request.values['userid']]={'password':request.values['userpw'],'nick':request.values['username']}
				with open('./member.json','w') as f:
					json.dump(member, f)
					basepath = os.path.join(os.path.dirname(__file__), 'static','uploads')
					os.mkdir(os.path.join(basepath,request.values['userid']))
				return render_template('index.html')
	return render_template('register.html')


@app.route('oldnewpage/login',methods=['GET','POST'])
def login():

	if request.method== 'POST' :
		with open('oldnewpage/member.json','r') as file_object:
			member = json.load(file_object)

		if request.values['userid'] in member:
			if member[request.values['userid']]['password']==request.values['userpw']:
				session['username']=request.values['userid']
				session['width']=request.values['bodywidth']
				return redirect ( url_for ( 'index' ))
			else:
				return render_template('login.html',alert="Your password is wrong, please check again!")
		else:
			return render_template('login.html',alert="Your account is unregistered.")
	return render_template('login.html')


@app.route('oldnewpage/logout',methods=['GET','POST'])
def logout ():
	if request.method=='POST':
		if request.values['send']=='確定':
			session.pop('username',None)
		return redirect(url_for('index'))
	return render_template('logout.html')

@app.route('oldnewpage/upload/',methods=['GET','POST'])
def upload():

	basepath = os.path.join(os.path.dirname(__file__), 'static','uploads')
	dirs=os.listdir(os.path.join(basepath,session.get('username')))
	dirs.insert(0,'New Folder')
	dirs.insert(0,'Not Choose')

	if request.method == 'POST':
		flist = request.files.getlist("file[]")
		
		for f in flist:
			try:
				basepath = os.path.join(os.path.dirname(__file__), 'static','uploads')
				format=f.filename[f.filename.index('.'):]
				fileName=time.time()
				if format in ('.jpg','.png','.jpeg','.HEIC','.jfif'):
					format='.jpg'
				else:
					format='.mp4'
					

				if request.values['folder']=='0':
					return render_template('upload.html',alert='Please choose a folder or creat a folder',dirs=dirs)

				elif request.values['folder']=='1':
					if not os.path.isdir(os.path.join(basepath,session.get('username'),request.values['foldername'])):
						os.mkdir(os.path.join(basepath,session.get('username'),request.values['foldername']))
						os.mkdir(os.path.join(basepath,session.get('username'),request.values['foldername'],'photo'))
						os.mkdir(os.path.join(basepath,session.get('username'),request.values['foldername'],'album'))
						os.mkdir(os.path.join(basepath,session.get('username'),request.values['foldername'],'album','photo'))

					if format == '.jpg':
						upload_path = os.path.join(basepath,session.get('username'),request.values['foldername'],'photo',str(fileName).replace('.','')+str(format))
						album_path = os.path.join(basepath,session.get('username'),request.values['foldername'],'album','photo',str(fileName).replace('.','')+str(format))
											
				else:
					if format == '.jpg':

						upload_path = os.path.join(basepath,session.get('username'),dirs[int(request.values['folder'])],'photo',str(fileName).replace('.','')+str(format))
						album_path = os.path.join(basepath,session.get('username'),dirs[int(request.values['folder'])],'album','photo',str(fileName).replace('.','')+str(format))
					
				f.save(upload_path)
				if format =='.mp4':
					video_photo(upload_path,album_path)
				else:
					image=cv2.imread(upload_path)
					fill_photo(image,album_path)

			except:
				return render_template('upload.html',alert='你沒有選擇要上傳的檔案',dirs=dirs)

		return redirect(url_for('upload'))
	return render_template('upload.html',dirs=dirs)

def video_photo(video_path,out_path):
	max_width=150

	cap = cv2.VideoCapture(video_path)
	video_width = int(cap.get(3))

	ratio = max_width * 1.0 / video_width

	ret, frame = cap.read()
	image=cv2.resize(frame, None, fx=ratio, fy=ratio)
	cap.release()

	cv2.imwrite(out_path, image)

def fill_photo(img,out_path):

	h,w=img.shape[0],img.shape[1]
	side=max(h,w)
	new = np.zeros((side,side,3), np.uint8)
	new.fill(255)
	if w>h:
		center=((side-h)/2.0)
		for i in range(img.shape[0]):
			for j in range(img.shape[1]):			
				new[int(i+center),j]=img[i,j]
	else:
		center=((side-w)/2.0)
		for i in range(img.shape[0]):
			for j in range(img.shape[1]):			
				new[i,int(j+center)]=img[i,j]
	cv2.imwrite(out_path, new)

@app.route('oldnewpage/album/', methods=['POST', 'GET'])
def album():

	colspan=int(int(session.get('width'))/150)
	if colspan>7:
		colspan=7
	basepath = os.path.join(os.path.dirname(__file__), 'static','uploads')
	dirs=os.listdir(os.path.join(basepath,session.get('username')))
	dirs.insert(0,'ALL')
	dirs.insert(0,'')

	dict2={} #record all folder has what number name

	for dir in dirs:
		if dir == "ALL" or dir == '':
			continue
		dict2[dir]={'photo':[],'video':[]}
		path=os.path.join(basepath,session.get('username'),dir,'photo')
		for lists in os.listdir(path):
			dict2[dir]['photo'].append(lists)

	if request.method == 'POST':
		if request.values['folder']!='0' and request.values['folder']!='1':
			return render_template('album.html',dirs=dirs,colspan=colspan, \
				filefolder=[dirs[int(request.values['folder'])]],files=dict2,username=session.get('username'))
		elif request.values['folder'] =='1':
			return render_template('album.html',dirs=dirs, colspan=colspan,\
				filefolder=dirs[2:],files=dict2,username=session.get('username'))
	return render_template('album.html',dirs=dirs, files=dict2, filefolder=dirs[2:],colspan=colspan,username=session.get('username'))

# @app.route('/menu/', methods=['POST', 'GET'])
# def menu():
# 	return render_template('album.html',dirs=dirs, files=dict2, filefolder=dirs[2:],colspan=colspan,username=session.get('username'))



if __name__ == '__main__':
	app.run(host='0.0.0.0',port='5000',debug=True)
