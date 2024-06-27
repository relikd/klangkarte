function validate_upload_limit(sender) {
    if (sender.files[0].size > sender.dataset.uploadLimit) {
        sender.value = '';
        alert(`Datei zu groß (max. ${sender.dataset.uploadLimitStr})`);
    }
}