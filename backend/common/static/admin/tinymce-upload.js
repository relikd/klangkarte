function tinymce_image_upload_handler(blobInfo, progress) {
    return new Promise((resolve, reject) => {
        const match = self.location.pathname.match('/app/place/([0-9]*)/');
        if (!match) {
            return reject('Cannot match place id from URL.');
        }

        // FIXME: this will still upload the image as base64 string
        // if (blobInfo.blob().size > 1_000_000) { // >1MB
        //     return reject('Image too large. Max file size: 1 MB');
        // }

        const placeId = match[1];
        let xhr, formData;
        // token = Cookies.get("csrftoken");
        token = document.cookie.match('csrftoken=([^;]*)')[1];
        xhr = new XMLHttpRequest();
        xhr.withCredentials = false;
        xhr.open('POST', '/tinymce/upload/' + placeId + '/');
        xhr.setRequestHeader('X-CSRFToken', token);

        if (progress) {
            xhr.upload.onprogress = function (e) {
                progress(e.loaded / e.total * 100);
            };
        }
        xhr.onload = function () {
            let json;

            if (xhr.status === 403) {
                return reject('HTTP Error: ' + xhr.status, { remove: true });
            }

            if (xhr.status < 200 || xhr.status >= 300) {
                return reject('HTTP Error: ' + xhr.status);
            }

            json = JSON.parse(xhr.responseText);

            if (!json || typeof json.location != 'string') {
                return reject('Invalid JSON: ' + xhr.responseText);
            }

            return resolve(json.location);
        };
        xhr.onerror = function () {
            return reject('Image upload failed due to a XHR Transport error. Code: ' + xhr.status);
        };

        formData = new FormData();
        formData.append('file', blobInfo.blob(), blobInfo.filename());

        xhr.send(formData);
    });
}
