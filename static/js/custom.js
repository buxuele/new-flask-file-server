document.addEventListener('DOMContentLoaded', function () {
    // 初始化图片画廊 GLightbox
    const lightbox = GLightbox({
        selector: '.glightbox',
        touchNavigation: true, // 在移动设备上启用滑动导航
        loop: true, // 循环播放
        autoplayVideos: true,
    });

    // 处理文件上传
    const uploadForm = document.getElementById('upload-form');
    const submitButton = document.getElementById('submit-upload');
    const uploadStatus = document.getElementById('upload-status');
    const fileInput = document.getElementById('file-input');
    const uploadModal = new bootstrap.Modal(document.getElementById('uploadModal'));

    if (submitButton) {
        submitButton.addEventListener('click', function () {
            if (fileInput.files.length === 0) {
                uploadStatus.innerHTML = `<div class="alert alert-warning">请先选择要上传的文件。</div>`;
                return;
            }

            // 显示加载状态并禁用按钮
            submitButton.disabled = true;
            submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 上传中...`;
            uploadStatus.innerHTML = '';

            const formData = new FormData(uploadForm);

            fetch(uploadForm.action, {
                method: 'POST',
                body: formData,
            })
            .then(response => {
                if (response.ok) {
                    return response.text(); // 或者 response.json() 如果后端返回 JSON
                }
                // 如果服务器返回错误，则抛出错误
                return response.text().then(text => { throw new Error(text) });
            })
            .then(data => {
                uploadStatus.innerHTML = `<div class="alert alert-success">文件上传成功！页面即将刷新。</div>`;
                // 2秒后关闭模态框并刷新页面
                setTimeout(() => {
                    uploadModal.hide();
                    location.reload();
                }, 2000);
            })
            .catch(error => {
                console.error('上传失败:', error);
                uploadStatus.innerHTML = `<div class="alert alert-danger">上传失败: ${error.message}</div>`;
            })
            .finally(() => {
                // 恢复按钮状态
                submitButton.disabled = false;
                submitButton.innerHTML = '开始上传';
            });
        });
    }
});