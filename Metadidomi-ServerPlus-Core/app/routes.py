from flask import Blueprint, request, jsonify, send_from_directory, abort
import os

bp = Blueprint('api', __name__)

@bp.route('/download/<path:filename>')
def download_file(filename):
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_uploads'))
    file_path = os.path.join(uploads_dir, filename)
    if not os.path.isfile(file_path):
        return f"Fichier introuvable : {filename}", 404
    try:
        return send_from_directory(uploads_dir, filename, as_attachment=True)
    except Exception as e:
        abort(500, f"Erreur lors du téléchargement : {e}")

@bp.route('/api/cloud_sync', methods=['POST'])
def cloud_sync():
    data = request.get_json()
    action = data.get('action')
    response = { 'success': False }
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metadidomi_cloud_storage_files', 'Root'))
    os.makedirs(root_dir, exist_ok=True)

    # Synchronisation des dossiers
    if action == 'create_folder':
        folder = data.get('folder')
        folder_path = os.path.join(root_dir, folder['name']) if not folder.get('parentId') else os.path.join(root_dir, folder['parentId'], folder['name'])
        try:
            os.makedirs(folder_path, exist_ok=False)
            response['success'] = True
        except FileExistsError:
            response['error'] = 'Dossier existe déjà'
    elif action == 'rename_folder':
        folderId = data.get('folderId')
        oldName = data.get('oldName')
        newName = data.get('newName')
        parent_path = os.path.join(root_dir, folderId) if folderId else root_dir
        old_path = os.path.join(parent_path, oldName)
        new_path = os.path.join(parent_path, newName)
        try:
            os.rename(old_path, new_path)
            response['success'] = True
        except Exception as e:
            response['error'] = str(e)
    elif action == 'delete_folder':
        folderId = data.get('folderId')
        folder_path = os.path.join(root_dir, folderId) if folderId else root_dir
        try:
            if os.path.exists(folder_path):
                import shutil
                shutil.rmtree(folder_path)
            response['success'] = True
        except Exception as e:
            response['error'] = str(e)
    # Synchronisation des fichiers
    elif action == 'upload_file':
        file = data.get('file')
        folder_path = os.path.join(root_dir, file['folderId']) if file.get('folderId') else root_dir
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, file['name'])
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file['content'])
            response['success'] = True
        except Exception as e:
            response['error'] = str(e)
    elif action == 'rename_file':
        fileId = data.get('fileId')
        oldName = data.get('oldName')
        newName = data.get('newName')
        folder_path = os.path.join(root_dir, fileId) if fileId else root_dir
        old_path = os.path.join(folder_path, oldName)
        new_path = os.path.join(folder_path, newName)
        try:
            os.rename(old_path, new_path)
            response['success'] = True
        except Exception as e:
            response['error'] = str(e)
    elif action == 'delete_file':
        fileId = data.get('fileId')
        fileName = data.get('fileName')
        folder_path = os.path.join(root_dir, fileId) if fileId else root_dir
        file_path = os.path.join(folder_path, fileName)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            response['success'] = True
        except Exception as e:
            response['error'] = str(e)
    else:
        response['error'] = 'Action inconnue'
    return jsonify(response)