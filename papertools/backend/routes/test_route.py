from flask import jsonify
from models import User  # 假设已定义 User 模型

@app.route('/test_db')
def test_db():
    try:
        # 尝试查询数据（若表存在）
        user = User.query.first()
        if user:
            return jsonify({"status": "success", "data": f"User: {user.username}"})
        else:
            # 若表为空，尝试创建一条测试数据
            new_user = User(username="test", email="test@example.com")
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"status": "success", "message": "Test user created"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})