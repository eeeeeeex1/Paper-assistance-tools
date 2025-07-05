# backend/routes/paper_route.py
from flask import Blueprint, request, jsonify,current_app,send_file,make_response  
from service.paper_service import PaperService
from flasgger import swag_from,Swagger
from backend.models.user import  User
from dao.paper_dao import PaperDao
from backend.config.database import db
from backend.models.paper import Paper # 导入相关模型
import os
from config.logging_config import logger
import urllib.parse
from config.config import BASE_DIR
import urllib.parse  # 用于编码文件名
from werkzeug.utils import secure_filename 
from flask_cors import CORS, cross_origin
import numpy as np

paper_bp = Blueprint('paper', __name__, url_prefix='/api/paper')
paper_service=PaperService()

def safe_delete_file(file_path, retries=3, delay=0.5):
    """安全删除文件，带有重试机制"""
    for i in range(retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"删除文件失败 ({i+1}/{retries}): {str(e)}")
            time.sleep(delay)
    
    print(f"无法删除文件: {file_path}")
    return False

@paper_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['论文管理'],
    'description': '获取所有论文',
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': '页码'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 10, 'description': '每页数量'}
    ],
    'responses': {
        200: {
            'description': '成功获取论文列表',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '成功获取论文列表'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'papers': {
                                'type': 'array',
                                'items': {
                                    '$ref': '#/definitions/Paper'
                                }
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_all_papers():
    """获取所有论文（支持分页）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    # 实际应调用控制器方法，此处为示例
    return jsonify({
        'code': 200,
        'message': '成功获取论文列表',
        'data': {'papers': []}
    })


@paper_bp.route('/upload', methods=['POST'])
@swag_from({
    'tags': ['论文管理'],
    'description': '上传论文',
    'consumes': ['multipart/form-data'],  # 修改为表单数据
    'parameters': [
        {
            'name': 'title',
            'in': 'formData',  # 修改为 formData
            'type': 'string',
            'required': True,
            'description': '论文标题'
        },
        {
            'name': 'author_id',
            'in': 'formData',  # 修改为 formData
            'type': 'integer',
            'required': True,
            'description': '作者ID'
        },
        {
            'name': 'file',
            'in': 'formData',  # 添加文件参数
            'type': 'file',
            'required': True,
            'description': '论文文件'
        }
    ],
    'responses': {
        201: {
            'description': '论文上传成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 201},
                    'message': {'type': 'string', 'example': '论文上传成功'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'paper_id': {'type': 'integer'},
                            'title': {'type': 'string'},
                            'upload_time': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {'description': '缺少必要参数'},
        500: {'description': '上传失败'}
    }
})
#zyb------------------------------------------------
def upload_paper():
    """上传论文文件并保存记录"""
    try:
        # 获取当前用户ID
        logger.info('begin upload#------------------------------------')
        user_id = request.form.get('user_id',type=int)
        
        # 验证请求包含文件
        if 'file' not in request.files:
            return jsonify({"error": "未找到文件"}), 400
        
        file = request.files['file']
        
        # 验证文件名
        if file.filename == '':
            return jsonify({"error": "空文件名"}), 400
        
        # 获取表单数据
        title = request.form.get('title', '未命名文件')
        logger.info("begin use service upload_paper")
        # 调用服务上传文件
        result = paper_service.upload_paper(
            file=file,
            title=title,
            author_id=user_id
        )
        logger.info(f'paper_id:{result}')
        return jsonify({
            "code": 200,
            "message": "文件上传成功",
            "data": result
        }), 201
    
    except ValueError as e:
        logger.error(f"上传失败: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"上传异常: {str(e)}", exc_info=True)
        return jsonify({"error": "服务器内部错误，请稍后再试"}), 500
#zyb------------------------------------------------


@paper_bp.route('/getpaperinfo', methods=['GET'])
@swag_from({
    'tags': ['论文管理'],
    'description': '获取单个论文信息',
    'parameters': [
        {'name': 'paper_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '论文ID'}
    ],
    'responses': {
        200: {
            'description': '成功获取论文信息',
            'schema': {
                '$ref': '#/definitions/PaperResponse'
            }
        },
        404: {'description': '论文不存在'}
    }
})
def get_paper(paper_id):
    """通过ID获取论文"""
    return paper_service.get_paper(paper_id)

@paper_bp.route('/<int:paper_id>', methods=['DELETE'])
@swag_from({
    'tags': ['论文管理'],
    'description': '删除论文',
    'parameters': [
        {'name': 'paper_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '论文ID'}
    ],
    'responses': {
        200: {
            'description': '删除成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '删除成功'}
                }
            }
        },
        400: {'description': '删除失败'},
        404: {'description': '论文不存在'}
    }
})
def delete_paper(paper_id):
    """删除论文"""
    return paper_service.delete_paper(paper_id)

@paper_bp.route('/user/<int:user_id>', methods=['GET'])
@swag_from({
    'tags': ['论文管理'],
    'description': '获取用户的所有论文',
    'parameters': [
        {'name': 'user_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '用户ID'},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': '页码'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 10, 'description': '每页数量'}
    ],
    'responses': {
        200: {
            'description': '成功获取用户论文列表',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '成功获取用户论文列表'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'user_info': {'$ref': '#/definitions/User'},
                            'papers': {
                                'type': 'array',
                                'items': {'$ref': '#/definitions/Paper'}
                            }
                        }
                    }
                }
            }
        },
        404: {'description': '用户不存在'}
    }
})
def get_user_papers(user_id):
    """获取指定用户的所有论文"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return paper_service.get_user_papers(user_id, page, per_page)
#--------------------------------------------------
#--------------------------------------------------------------------    
@paper_bp.route('/spelling', methods=['POST'])
@swag_from({
    'tags': ['论文管理'],
    'description': '论文错字检测',
    'parameters': [
        {'name': 'paper_id', 'in': 'path', 'type': 'integer', 'required': True, 'description': '论文ID'}
    ],
    'responses': {
        200: {
            'description': '错字检测完成',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'message': {'type': 'string', 'example': '错字检测完成'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'error_count': {'type': 'integer'},
                            'sample_errors': {'type': 'array', 'items': {'type': 'string'}},
                            'suggestions': {'type': 'array', 'items': {'type': 'string'}}
                        }
                    }
                }
            }
        },
        400: {'description': '检测失败'},
        404: {'description': '论文不存在'}
    }
})

def check_spelling():
    """论文错字检测API接口"""
    logger.info("get spelling request----------------------------")
    
    # 1. 检查文件上传
    if 'file' not in request.files:
        logger.warning("request no file")
        return jsonify({
            'code': 400,
            'message': '未上传文件'
        }), 400
        
    file = request.files['file']
    user_id=request.form.get('user_id',type=int)
    paper_id = request.form.get('paper_id', type=int)

    if file.filename == '':
        logger.warning("上传文件名为空")
        return jsonify({
            'code': 400,
            'message': '文件名为空'
        }), 400

    # 检查文件类型
    if not file.filename.endswith(('.txt', '.doc', '.docx')):
        return jsonify({
                'code': 400,
                'message': '不支持的文件格式，仅支持 .txt, .doc, .docx'
        }), 400
            
    # 2. 调用服务层处理
    try:
        logger.info("go wrong service")
        success, result = paper_service.check_spelling(file,user_id,paper_id)
        
        if success:
            logger.info(f"spelling finish,find {len(result['typo_details'])} wrongs")
            return jsonify({
                'code': 200,
                'message': '错字检测完成',
                'data': result
            }), 200
        else:
            
            return jsonify({
                'code': 400,
                'message': result
            }), 400
            
    except Exception as e:
        logger.error(f"jiekouwrong: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500



@paper_bp.route('/plagiarism', methods=['POST'])
@swag_from({
    'tags': ['论文管理'],
    'description': '论文查重，直接上传文件计算相似度',
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': '上传的论文文件'
        },
        {
            'name': 'num_articles',
            'in': 'formData',
            'type': 'integer',
            'default': 5,
            'description': '爬取的相似文章数量'
        }
    ],
    'responses': {
        200: {
            'description': '查重完成，返回相似度结果',
            'schema': {
                'type': 'object',
                'properties': {
                    'code': 200,
                    'message': '查重完成',
                    'data': {
                        'comprehensive_similarity': 25.63,
                        'paper_title': '人工智能在医疗中的应用',
                        'keywords': ['人工智能', '医疗'],
                        # 其他字段...
                    }
                }
            }
        },
        400: {'description': '缺少文件或参数错误'},
        500: {'description': '服务器内部错误'}
    }
})
def check_plagiarism():
    logger.info("begin check plagiarism with file upload------------------")

    # 获取上传的文件
    file = request.files.get('file')
    if not file:
        return jsonify({
            'code': 400,
            'message': '未上传论文文件',
            'data': None
        }), 400
    
    # 获取查询参数
    num_articles = request.form.get('num_articles', 5, type=int)
    
    checkfunction=request.form.get('checkfunction',type=str)
    user_id=request.form.get('user_id',type=int)
    paper_id = request.form.get('paper_id', type=int)
    logger.info(f'checkfunction:{checkfunction}')
    logger.info(f'paper________________data:{paper_id}')
    try:
        # 调用服务层方法
        if(checkfunction=='webSearch'):
            result = paper_service.check_plagiarism(file, num_articles,user_id,paper_id)
        if(checkfunction=='databaseSearch'):
            result = paper_service.check_plagiarism_ai(file, num_articles,user_id)
        
        def convert_numpy_types(data):
            """把NumPy数据类型转换为Python内置类型"""
            if isinstance(data, dict):
                return {k: convert_numpy_types(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_numpy_types(v) for v in data]
            elif isinstance(data, np.number):
                return data.item()  # 把NumPy数值转换为Python类型
            elif isinstance(data, np.ndarray):
                return data.tolist()  # 把NumPy数组转换为Python列表
            else:
                return data
        
        # 转换NumPy类型-------li
        result = convert_numpy_types(result)

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"查重失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '查重过程中服务器错误',
            'data': None
        }), 500
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"查重失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '查重过程中服务器错误',
            'data': None
        }), 500

@paper_bp.route('/theme', methods=['POST'])
def extract_theme():
    logger.info("begin 111111 extract theme")
    
    if 'file' not in request.files:
        return jsonify({
            'code': 400,
            'message': '未上传文件'
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'code': 400,
            'message': '文件名为空'
        }), 400
    #获取查询参数
    user_id=request.form.get('user_id',type=int)
    paper_id = request.form.get('paper_id', type=int)
    try:
        # 调用服务层方法
        result = paper_service.extract_theme(file,user_id,paper_id)
        return jsonify(result), result.get('code', 500)
    except Exception as e:
        # 记录详细的错误堆栈信息
        import traceback
        logger.error(f"调用服务层方法时发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'code': 500,
            'message': f'服务器内部错误: {str(e)}'
        }), 500
#-----------------------------------------------------------------------------------
#lmk-----------------------------------------------------------------------------------
@paper_bp.route('/total_count', methods=['GET'])
def get_total_paper_count():
    """获取上传的论文总数"""
    try:
        logger.info("开始获取论文总数")
        total_count = paper_service.get_total_paper_count()
        return jsonify({
            'code': 200,
            'message': '获取论文总数成功',
            'data': {
                'total_count': total_count
            }
        }), 200
    except Exception as e:
        logger.error(f"获取论文总数失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取论文总数失败: {str(e)}'
        }), 500
#lmk-----------------------------------------------------------------------------------

#zyb---------------------------------------------------------

@paper_bp.route('/downloadPaper', methods=['GET'])
@cross_origin(
    allow_headers=['Content-Disposition', 'Authorization'],  # 允许 Authorization 头
    expose_headers=['Content-Disposition']  # 允许前端访问的响应头
)
def download_file():
    # 从查询参数获取 paper_id 并校验
    paper_id = request.args.get('paper_id')
    logger.info(f'开始处理文件下载，paper_id: {paper_id}')
    if not paper_id:
        logger.error('缺少 paper_id 参数')
        return jsonify({"error": "缺少paper_id参数"}), 400
    
    try:
        # 从数据库查询文件记录
        paper = Paper.query.get(paper_id)
        base_path = r'c:\\Users\\lenovo\\Desktop\\papertools7.2\\backend\\config\\'
        if not paper or not paper.file_path:
            logger.error('文件记录不存在或路径为空')
            return jsonify({"error": "文件不存在01"}), 404
        
        # 拼接完整路径并校验文件存在性
        file_path = os.path.join(base_path, paper.file_path)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            logger.error(f'文件路径 {file_path} 不存在或非文件')
            return jsonify({"error": "文件不存在或无法访问02"}), 404
        
        # 处理文件名与扩展名
        filename = os.path.basename(file_path)
        # 优先用 secure_filename 处理文件名，增强兼容性与安全性
        filename = secure_filename(filename)  
        file_ext = os.path.splitext(filename)[1].lower()
        
        # 映射文件扩展名到 Content-Type
        content_type_map = {
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.jpg': 'image/jpeg',
            '.png': 'image/png'
        }
        content_type = content_type_map.get(file_ext, 'application/octet-stream')
        
        # 文件名编码（兼容各类浏览器）
        def get_content_disposition(name):
            # 现代浏览器用 filename* 语法
            utf8_name = urllib.parse.quote(name)
            # 旧版浏览器 fallback（若有特殊字符可能仍有问题，但尽量兼容）
            ascii_name = urllib.parse.quote(name.encode('utf-8', errors='replace').decode('utf-8'))  
            return f"attachment; filename*=UTF-8''{utf8_name}; filename=\"{ascii_name}\""
        
        # 构建响应
        response = make_response()
        # 二进制读取文件内容，with 语法确保文件句柄关闭
        with open(file_path, 'rb') as f:
            response.data = f.read()
        
        # 设置响应头
        response.headers['Content-Type'] = content_type
        response.headers['Content-Length'] = str(os.path.getsize(file_path))  # 转字符串，确保格式正确
        response.headers['Content-Disposition'] = get_content_disposition(filename)
        # 禁用缓存，避免浏览器复用旧响应
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers.add('Access-Control-Allow-Headers', 'Content-Disposition, Authorization')
        response.headers.add('Access-Control-Expose-Headers', 'Content-Disposition')
        
        logger.info(f'文件 {filename} 下载响应构建完成，即将返回')
        logger.info(f"响应头设置完成：\n"
                    f"  Content-Type: {content_type}\n"
                    f"  Content-Disposition: {response.headers['Content-Disposition']}\n")
        
        logger.info("===== 文件下载响应已发送 =====")

        return response
        
    except Exception as e:
        logger.error(f'下载文件失败: {str(e)}', exc_info=True)  # exc_info 记录详细异常栈
        return jsonify({"error": "下载文件失败"}), 500
#zyb---------------------------------------------------------


#lzj----------------------------------------------------------------------------------
@paper_bp.route('/check_local_plagiarism', methods=['POST'])
def check_local_plagiarism():
    # 检查是否有文件上传
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "请上传两个文件"}), 400
    logger.info('begin controller check')
    file1 = request.files['file1']
    file2 = request.files['file2']
    user_id=request.form.get('user_id',type=int)
    # 检查文件是否有名称（即是否真的上传了文件）
    if file1.filename == '' or file2.filename == '':
        return jsonify({"error": "上传的文件不能为空"}), 400
    
    try:
        # 假设check_local_plagiarism返回字典类型
        result = paper_service.check_local_plagiarism(file1,file2,user_id)
        # 获取并记录比较结果列表
        result_data = result.get("data", {})
        comparison_results = result.get("data", {}).get("comparison_results", [])
        logger.info(f"Comparison Results: {comparison_results}")

        # 获取并记录综合相似度
        comprehensive_similarity = result.get("data", {}).get("comprehensive_similarity")
        logger.info(f"Comprehensive Similarity: {comprehensive_similarity}")
                # 使用jsonify将结果转换为JSON响应
        return jsonify({
            "code": 200,
            "message": "查重成功",
            "data": {
                "comparison_results": result_data.get("comparison_results", []),
                "comprehensive_similarity": result_data.get("comprehensive_similarity", 0.0)
            }
        })
    except Exception as e:
        # 记录详细错误日志
        logger.error(f"查重失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500,
            "error": "服务器内部错误，请稍后再试"
        }), 500