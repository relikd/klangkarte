
TINYMCE_DEFAULT_CONFIG = {
    "width": "100%",

    # see https://www.tiny.cloud/docs/tinymce/latest/available-menu-items/
    "menubar": "edit view insert format table help",  # file tools

    "plugins": "advlist autolink lists link image charmap anchor "
    "searchreplace visualblocks code fullscreen insertdatetime media table "
    "help",  # paste print preview wordcount

    # see https://www.tiny.cloud/docs/tinymce/latest/available-toolbar-buttons/
    "toolbar": "undo redo | blocks | bold italic removeformat | "
    "bullist numlist outdent indent",
    # forecolor backcolor | alignleft aligncenter alignright alignjustify

    "promotion": False,  # hide upgrade button
    "language": "de_DE",
    # "custom_undo_redo_levels": 10,

    "images_file_types": 'jpeg,jpg,png,gif',
    "images_upload_handler": "tinymce_image_upload_handler",
    "images_reuse_filename": True,  # prevent image edits from reuploading imgs
    "convert_urls": False,
}

TINYMCE_EXTRA_MEDIA = {
    'css': {'all': []},
    'js': ['admin/tinymce-upload.js'],
}
