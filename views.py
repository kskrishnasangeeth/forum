import app,models,forms,utils
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required


class Forum(app.request):
  def get(self):
    data = {'list':models.getForums()}
    self.show('forum',data)


class Topics(app.request):
  def get(self,fid):
    forum  = models.getForum(fid)
    topics = models.getTopics(fid)
    data   = {'forum':forum,'list':topics}
    self.show('topics',data)


class NewTopic(app.request):
  @login_required
  def get(self,fid):
    user = users.get_current_user()
    data={
      'forum':models.getForum(fid),
      'author':utils.getNick(user.nickname())
    }
    self.show('topics_new',data)

  def post(self,fid):
    form = forms.newTopic(self,fid)
    if form.ok or form.redirect:
      self.redirect(form.url)
    else:
      self.show('topics_new',form.data)


class Messages(app.request):
  def get(self,fid,tid):
    data = models.viewMessages(fid,tid)
    user = users.get_current_user()
    if user: data['author']=utils.getNick(user.nickname())
    self.show('messages',data)

  def post(self,fid,tid):
    form = forms.messages(self,fid,tid)
    if form.ok or form.redirect:
      self.redirect(form.url)
    else:
      self.show('messages',form.data)


class MyProfile(app.request):
  @login_required
  def get(self):
    user = users.get_current_user()
    uid  = user.user_id()
    profile = models.getUser(uid)
    if not profile: 
      nick = user.nickname()
      mail = ''
      if '@' in nick:
        mail  = nick
        nick  = utils.getNick(nick)
      isadmin = users.is_current_user_admin()
      ip      = self.ipaddress
      profile = models.newEmptyUser(uid,nick,mail,isadmin,ip)
    data={'profile':profile}
    self.show('myprofile',data)

  def post(self):
    form = forms.myprofile(self)
    if form.ok or form.redirect:
      self.redirect(form.url)
    else:
      self.show('myprofile',form.data)

class Profiles(app.request):
  def get(self,uid):
    user = models.getUser(uid)
    data = {'user':user,'userid':uid}
    self.show('profile',data)


class ImageHandler(app.request):
  def get(self,id):
    if not id:
      self.error(404)
      return
    img = models.Images.get_by_key_name(id)
    if not img: 
      self.error(404)
      return
    #TODO memcache image
    self.response.headers['Content-Type']  = img.format
    self.response.headers['Cache-Control'] = 'max-age=1000000' # two weeks
    self.response.out.write(img.bits) 


class NotFound(app.request):
  def get(self):
    self.show('notfound')


#---- END ----
