import os

from kivy.utils import platform

from textstoryreader.constants import (
    REQUEST_CODE_PICK_FILE,
    REQUEST_CODE_PICK_FOLDER,
    SUPPORTED_EXTENSIONS,
)

# Các lớp Android cần thiết từ Jnius
PythonActivity = None
Intent = None
Uri = None
Environment = None
DocumentsContract = None
ContentResolver = None
DocumentFile = None
Environment = None
PythonJavaClass = None
java_method = None
RESULT_OK = -1  # Android's Activity.RESULT_OK (Java-side)
RESULT_CANCELED = 0  # Android's Activity.RESULT_CANCELED (Java-side)

if platform == "android":
    print("DEBUG: Nền tảng được nhận diện là Android. Đang cố gắng import Jnius...")
    try:
        from jnius import PythonJavaClass, autoclass, java_method

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        DocumentFile = autoclass("androidx.documentfile.provider.DocumentFile")
        Environment = autoclass("android.os.Environment")

        class AndroidIntentHandler(PythonJavaClass):
            __javainterfaces__ = ["org.kivy.android.PythonActivity$ActivityResultListener"]
            __javacontext__ = "app"

            def __init__(self, callback, **kwargs):
                super().__init__(**kwargs)
                self.callback = callback
                print("DEBUG: AndroidIntentHandler initialized.")

            @java_method("(IILandroid/content/Intent;)V")
            def onActivityResult(self, requestCode, resultCode, intent):
                print(f"DEBUG: onActivityResult received - RequestCode: {requestCode}, ResultCode: {resultCode}")
                if resultCode == RESULT_OK and intent is not None:
                    data_uri = intent.getData()
                    if data_uri is not None:
                        self.callback(requestCode, resultCode, data_uri)
                    else:
                        print("DEBUG: Intent data (URI) is None.")
                        self.callback(requestCode, resultCode, None)  # Truyền None nếu không có URI
                elif resultCode == RESULT_CANCELED:
                    print("DEBUG: User cancelled the action.")
                    self.callback(requestCode, resultCode, None)  # Truyền None nếu người dùng hủy
                else:
                    print(f"DEBUG: onActivityResult - Unexpected resultCode: {resultCode} or Intent is None.")
                    self.callback(requestCode, resultCode, None)

    except Exception as e:
        import traceback

        print(f"ERROR: Jnius imports failed: {type(e).__name__}: {e}")
        print(traceback.format_exc())  # In ra full traceback để debug
        print("ERROR: Running in non-Android compatibility mode.")
        PythonActivity = None


class AndroidHandle:
    def get_android_paths(self):
        self.book_folder_path = None
        try:
            context = PythonActivity.mActivity
            # Lấy đường dẫn tới thư mục tài liệu riêng tư của ứng dụng
            app_private_docs_dir = context.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS).getAbsolutePath()
            self.book_folder_path = os.path.join(app_private_docs_dir, "TextStoryReader", "books")
            print(f"DEBUG (BookManager): Thiết lập self.book_folder_path Android (App Private): {self.book_folder_path}")
        except Exception as e:
            print(f"Lỗi khi lấy đường dẫn Android: {e}. Đang dùng đường dẫn mặc định.")
        return self.book_folder_path

    def _ensure_folders_exist(self):
        try:
            os.makedirs(self.book_folder_path, exist_ok=True)
            print(f"DEBUG (BookManager): Đã đảm bảo thư mục sách '{self.book_folder_path}' tồn tại.")
        except Exception as e:
            print(f"Lỗi khi tạo thư mục sách '{self.book_folder_path}': {e}")

    def pick_file(self):
        if not self.is_android:
            self._report_status("Chức năng chỉ có trên Android.")
            return

        try:
            current_activity = PythonActivity.mActivity

            # Đảm bảo listener cũ được gỡ bỏ trước khi tạo cái mới nếu có
            if self.android_intent_handler:
                current_activity.unregisterActivityResultListener(self.android_intent_handler)
                self.android_intent_handler = None

            # Khởi tạo Intent Handler cho callback cụ thể cho chọn file
            self.android_intent_handler = AndroidIntentHandler(self._handle_android_intent_result)
            current_activity.registerActivityResultListener(self.android_intent_handler)

            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("text/*")
            current_activity.startActivityForResult(intent, REQUEST_CODE_PICK_FILE)
            print("DEBUG: Đã khởi chạy Intent chọn tệp.")

        except Exception as e:
            print(f"Lỗi khi khởi chạy Intent chọn tệp: {e}")
            self._report_status(f"Lỗi khởi chạy chọn tệp: {e}")
            # Đảm bảo gỡ listener nếu có lỗi ngay sau khi khởi chạy Intent
            if self.android_intent_handler:
                current_activity.unregisterActivityResultListener(self.android_intent_handler)
                self.android_intent_handler = None

    def pick_folder(self):
        if not self.is_android:
            self._report_status("Chức năng chỉ có trên Android.")
            return

        try:
            current_activity = PythonActivity.mActivity

            # Đảm bảo listener cũ được gỡ bỏ trước khi tạo cái mới nếu có
            if self.android_intent_handler:
                current_activity.unregisterActivityResultListener(self.android_intent_handler)
                self.android_intent_handler = None

            # Khởi tạo Intent Handler cho callback cụ thể cho chọn folder
            self.android_intent_handler = AndroidIntentHandler(self._handle_android_intent_result)
            current_activity.registerActivityResultListener(self.android_intent_handler)

            intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
            current_activity.startActivityForResult(intent, REQUEST_CODE_PICK_FOLDER)
            print("DEBUG: Đã khởi chạy Intent chọn thư mục.")

        except Exception as e:
            print(f"Lỗi khi khởi chạy Intent chọn thư mục: {e}")
            self.report_status(f"Lỗi khởi chạy chọn thư mục: {e}")
            # Đảm bảo gỡ listener nếu có lỗi ngay sau khi khởi chạy Intent
            if self.android_intent_handler:
                current_activity.unregisterActivityResultListener(self.android_intent_handler)
                self.android_intent_handler = None

    def _handle_android_intent_result(self, requestCode, resultCode, uri):
        """
        Callback chung cho cả chọn file và chọn folder.
        Phân biệt hành động dựa vào requestCode.
        """
        print(f"DEBUG: _handle_android_intent_result received - RequestCode: {requestCode}, ResultCode: {resultCode}, URI: {uri}")

        # Luôn gỡ listener sau khi nhận kết quả để tránh rò rỉ bộ nhớ
        # và để đảm bảo mỗi yêu cầu Intent có một listener riêng
        if self.android_intent_handler:
            try:
                PythonActivity.mActivity.unregisterActivityResultListener(self.android_intent_handler)
                print("DEBUG: android_intent_handler removed.")
            except Exception as e:
                print(f"ERROR: Could not remove android_intent_handler: {e}")
            finally:
                self.android_intent_handler = None  # Đặt lại để chuẩn bị cho lần chọn tiếp theo

        if resultCode == RESULT_CANCELED or uri is None:
            self._report_status("Người dùng đã hủy hoặc không có dữ liệu được chọn.")
            return

        if requestCode == REQUEST_CODE_PICK_FILE:
            self._handle_file_pick_result_internal(uri)
        elif requestCode == REQUEST_CODE_PICK_FOLDER:
            self._handle_folder_pick_result_internal(uri)
        else:
            self._report_status(f"RequestCode không xác định: {requestCode}")
            print(f"WARNING: Unknown requestCode received: {requestCode}")

    def _handle_file_pick_result_internal(self, uri):
        """Logic xử lý kết quả chọn file."""
        print(f"DEBUG: Xử lý kết quả chọn tệp: {uri}")
        try:
            context = PythonActivity.mActivity
            content_resolver = context.getContentResolver()

            display_name = "unknown_file"
            try:
                # Đảm bảo đóng cursor sau khi sử dụng
                with content_resolver.query(uri, None, None, None, None) as cursor:
                    if cursor is not None and cursor.moveToFirst():
                        display_name_column_index = cursor.getColumnIndex(autoclass("android.provider.OpenableColumns").DISPLAY_NAME)
                        if display_name_column_index != -1:
                            display_name = cursor.getString(display_name_column_index)
                            print(f"DEBUG: Found display name: {display_name}")
            except Exception as e_cursor:
                print(f"Lỗi khi lấy tên hiển thị từ URI: {e_cursor}")

            # Tạo đường dẫn đích trong thư mục sách của ứng dụng
            dest_file_path = os.path.join(self.book_folder_path, display_name)

            # Copy nội dung từ URI sang tệp đích
            with content_resolver.openInputStream(uri) as input_stream:
                with open(dest_file_path, "wb") as output_stream:
                    buffer = bytearray(4096)  # Kích thước buffer 4KB
                    bytes_read = input_stream.read(buffer)
                    while bytes_read != -1:
                        if bytes_read > 0:
                            output_stream.write(buffer[:bytes_read])
                        bytes_read = input_stream.read(buffer)
            print(f"DEBUG: Đã sao chép tệp '{display_name}' vào '{dest_file_path}'")

            self._report_status(f"Đã nhập sách: {display_name}")
            self._trigger_ui_update()  # Yêu cầu UI cập nhật danh sách sách

        except Exception as e:
            print(f"Lỗi khi xử lý tệp đã chọn: {e}")
            self._report_status(f"Lỗi nhập sách: {e}")

    def _handle_folder_pick_result_internal(self, uri):
        """Logic xử lý kết quả chọn folder."""
        print(f"DEBUG: Xử lý kết quả chọn thư mục: {uri}")
        try:
            context = PythonActivity.mActivity

            # Lấy DocumentFile đại diện cho thư mục đã chọn
            root_document = DocumentFile.fromTreeUri(context, uri)

            if root_document is None:
                print("Lỗi: Không thể lấy DocumentFile từ URI.")
                self._report_status("Lỗi: Không thể chọn thư mục.")
                return

            # Giữ quyền truy cập URI (Rất quan trọng cho SAF)
            # persistent_permissions = Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
            # context.getContentResolver().takePersistableUriPermission(uri, persistent_permissions)
            # Lưu URI này vào config file hoặc lưu trữ cục bộ để có thể truy cập lại sau này

            self._process_document_tree(root_document)
            self._report_status(f"Đã nhập sách từ thư mục: {root_document.getName()}")
            self._trigger_ui_update()  # Yêu cầu UI cập nhật danh sách sách

        except Exception as e:
            print(f"Lỗi khi xử lý thư mục đã chọn: {e}")
            self._report_status(f"Lỗi nhập thư mục: {e}")

    def _process_document_tree(self, document_file_root):
        """
        Đệ quy duyệt qua cây thư mục DocumentFile và copy các tệp hợp lệ.
        """
        if not document_file_root.isDirectory():
            return  # Chỉ xử lý thư mục

        for child_document in document_file_root.listFiles():
            if child_document.isDirectory():
                self._process_document_tree(child_document)
            elif child_document.isFile():
                file_name = child_document.getName()

                if any(file_name.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                    try:
                        dest_file_path = os.path.join(self.book_folder_path, file_name)

                        context = PythonActivity.mActivity
                        content_resolver = context.getContentResolver()

                        with content_resolver.openInputStream(child_document.getUri()) as input_stream:
                            with open(dest_file_path, "wb") as output_stream:
                                buffer = bytearray(4096)
                                bytes_read = input_stream.read(buffer)
                                while bytes_read != -1:
                                    if bytes_read > 0:
                                        output_stream.write(buffer[:bytes_read])
                                    bytes_read = input_stream.read(buffer)
                        print(f"DEBUG: Đã sao chép tệp '{file_name}' vào '{dest_file_path}'")
                    except Exception as e:
                        print(f"Lỗi khi sao chép tệp '{file_name}': {e}")
                else:
                    print(f"DEBUG: Bỏ qua tệp không hợp lệ: {file_name}")
