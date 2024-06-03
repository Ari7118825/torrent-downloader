from flask import Flask, request, render_template, jsonify
import libtorrent as lt
import time
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def download_torrent(torrent_path, save_path):
    ses = lt.session()
    ses.listen_on(6881, 6891)
    
    info = lt.torrent_info(torrent_path)
    h = ses.add_torrent({'ti': info, 'save_path': save_path})
    print('Starting download for:', h.name())
    
    while not h.is_seed():
        s = h.status()
        print(f'Download rate: {s.download_rate / 1000} kB/s, Upload rate: {s.upload_rate / 1000} kB/s, Progress: {s.progress * 100:.2f}%')
        time.sleep(1)
    
    print('Download complete:', h.name())
    return h.name()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    if 'torrent_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    file = request.files['torrent_file']
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    torrent_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(torrent_path)
    
    try:
        downloaded_file = download_torrent(torrent_path, DOWNLOAD_FOLDER)
        return jsonify({'status': 'success', 'downloaded_file': downloaded_file})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
