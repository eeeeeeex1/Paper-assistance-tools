from controllers.user_controller import UserController

class UserService:
    @staticmethod
    def register_user(username, password, email):
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            return False, "用户名已存在"
        
        # 创建新用户
        new_user = User(username=username, password_hash=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        return True, "注册成功"

    @staticmethod
    def login_user(username, password):
        # 查询用户
        user = User.query.filter_by(username=username).first()
        if user and user.password_hash == password:
            return True, "登录成功", user
        else:
            return False, "用户名或密码错误", None

    @staticmethod
    def get_user_info(user_id):
        # 获取用户信息
        user = User.query.get(user_id)
        if user:
            return True, user
        else:
            return False, "用户不存在"