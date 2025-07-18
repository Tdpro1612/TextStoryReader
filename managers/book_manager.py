import os

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.utils import platform

from managers.constants import (
    REQUEST_CODE_PICK_FILE,
    REQUEST_CODE_PICK_FOLDER,
    SUPPORTED_EXTENSIONS,
)
from services.parsers.parser_html import read_book_html
from services.parsers.parser_txt import read_book_txt

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
        # Import Androidx DocumentFile
        DocumentFile = autoclass("androidx.documentfile.provider.DocumentFile")
        # Import Android Environment class for standard directories
        Environment = autoclass("android.os.Environment")

        # Định nghĩa Activity Result Listener cho Android
        class AndroidIntentHandler(PythonJavaClass):
            # __javainterfaces__ để triển khai một giao diện Java
            __javainterfaces__ = [
                "org.kivy.android.PythonActivity$ActivityResultListener"
            ]
            __javacontext__ = "app"  # 'app' là ngữ cảnh mặc định cho PythonActivity

            def __init__(self, callback, **kwargs):
                super().__init__(**kwargs)
                self.callback = callback
                print("DEBUG: AndroidIntentHandler initialized.")

            @java_method("(IILandroid/content/Intent;)V")
            def onActivityResult(self, requestCode, resultCode, intent):
                print(
                    f"DEBUG: onActivityResult received - RequestCode: {requestCode}, ResultCode: {resultCode}"
                )
                if resultCode == RESULT_OK and intent is not None:
                    data_uri = intent.getData()
                    if data_uri is not None:
                        self.callback(requestCode, resultCode, data_uri)
                    else:
                        print("DEBUG: Intent data (URI) is None.")
                        self.callback(
                            requestCode, resultCode, None
                        )  # Truyền None nếu không có URI
                elif resultCode == RESULT_CANCELED:
                    print("DEBUG: User cancelled the action.")
                    self.callback(
                        requestCode, resultCode, None
                    )  # Truyền None nếu người dùng hủy
                else:
                    print(
                        f"DEBUG: onActivityResult - Unexpected resultCode: {resultCode} or Intent is None."
                    )
                    self.callback(
                        requestCode, resultCode, None
                    )  # Trường hợp khác, truyền None

    except Exception as e:
        # In ra loại lỗi và thông điệp lỗi cụ thể
        import traceback

        print(f"ERROR: Jnius imports failed: {type(e).__name__}: {e}")
        print(traceback.format_exc())  # In ra full traceback để debug
        print("ERROR: Running in non-Android compatibility mode.")
        PythonActivity = None


class BookManager:
    
    def __init__(self, **kwargs):
        self.book_folder_path = os.path.join(os.getcwd(), "books")
        self.is_android = False
        self.android_intent_handler = None  # Khởi tạo ban đầu là None

        # Callbacks cho UI (sẽ được App thiết lập)
        self.status_callback = None
        self.update_book_list_callback = None

        if (
            platform == "android" and PythonActivity
        ):  # Kiểm tra cả platform và PythonActivity có tồn tại không
            self.is_android = True
            print(
                "DEBUG (BookManager): Đang chạy trên Android, thiết lập đường dẫn Android."
            )
            self._get_android_paths()

        print(
            f"DEBUG (BookManager): Thư mục sách (self.book_folder_path): {self.book_folder_path}"
        )

        # Đảm bảo các thư mục tồn tại
        self._ensure_folders_exist()

    # Phương thức để App thiết lập callbacks
    def set_ui_callbacks(self, status_callback, update_book_list_callback):
        self.status_callback = status_callback
        self.update_book_list_callback = update_book_list_callback
        print("DEBUG (BookManager): UI callbacks đã được thiết lập.")

    def _report_status(self, message):
        """Báo cáo trạng thái về UI thông qua callback."""
        if self.status_callback:
            # Đặt lịch để callback chạy trên luồng chính của Kivy
            Clock.schedule_once(lambda dt: self.status_callback(message))
        else:
            print(
                f"BookManager Status: {message}"
            )  # Fallback nếu callback chưa được thiết lập

    def _trigger_ui_update(self):
        """Yêu cầu UI cập nhật danh sách sách."""
        if self.update_book_list_callback:
            # Đặt lịch để callback chạy trên luồng chính của Kivy
            Clock.schedule_once(lambda dt: self.update_book_list_callback())
        else:
            print("BookManager: UI update callback not set.")  # Fallback

    def _get_android_paths(self):
        try:
            context = PythonActivity.mActivity
            # Lấy đường dẫn tới thư mục tài liệu riêng tư của ứng dụng
            app_private_docs_dir = context.getExternalFilesDir(
                Environment.DIRECTORY_DOCUMENTS
            ).getAbsolutePath()
            self.book_folder_path = os.path.join(
                app_private_docs_dir, "TextStoryReader", "books"
            )
            print(
                f"DEBUG (BookManager): Thiết lập self.book_folder_path Android (App Private): {self.book_folder_path}"
            )
        except Exception as e:
            print(f"Lỗi khi lấy đường dẫn Android: {e}. Đang dùng đường dẫn mặc định.")

    def _ensure_folders_exist(self):
        """Đảm bảo các thư mục cần thiết tồn tại."""
        try:
            os.makedirs(self.book_folder_path, exist_ok=True)
            print(
                f"DEBUG (BookManager): Đã đảm bảo thư mục sách '{self.book_folder_path}' tồn tại."
            )
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
                current_activity.unregisterActivityResultListener(
                    self.android_intent_handler
                )
                self.android_intent_handler = None

            # Khởi tạo Intent Handler cho callback cụ thể cho chọn file
            self.android_intent_handler = AndroidIntentHandler(
                self._handle_android_intent_result
            )
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
                current_activity.unregisterActivityResultListener(
                    self.android_intent_handler
                )
                self.android_intent_handler = None

    def pick_folder(self):
        if not self.is_android:
            self._report_status("Chức năng chỉ có trên Android.")
            return

        try:
            current_activity = PythonActivity.mActivity

            # Đảm bảo listener cũ được gỡ bỏ trước khi tạo cái mới nếu có
            if self.android_intent_handler:
                current_activity.unregisterActivityResultListener(
                    self.android_intent_handler
                )
                self.android_intent_handler = None

            # Khởi tạo Intent Handler cho callback cụ thể cho chọn folder
            self.android_intent_handler = AndroidIntentHandler(
                self._handle_android_intent_result
            )
            current_activity.registerActivityResultListener(self.android_intent_handler)

            intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
            current_activity.startActivityForResult(intent, REQUEST_CODE_PICK_FOLDER)
            print("DEBUG: Đã khởi chạy Intent chọn thư mục.")

        except Exception as e:
            print(f"Lỗi khi khởi chạy Intent chọn thư mục: {e}")
            self.report_status(f"Lỗi khởi chạy chọn thư mục: {e}")
            # Đảm bảo gỡ listener nếu có lỗi ngay sau khi khởi chạy Intent
            if self.android_intent_handler:
                current_activity.unregisterActivityResultListener(
                    self.android_intent_handler
                )
                self.android_intent_handler = None

    def _handle_android_intent_result(self, requestCode, resultCode, uri):
        """
        Callback chung cho cả chọn file và chọn folder.
        Phân biệt hành động dựa vào requestCode.
        """
        print(
            f"DEBUG: _handle_android_intent_result received - RequestCode: {requestCode}, ResultCode: {resultCode}, URI: {uri}"
        )

        # Luôn gỡ listener sau khi nhận kết quả để tránh rò rỉ bộ nhớ
        # và để đảm bảo mỗi yêu cầu Intent có một listener riêng
        if self.android_intent_handler:
            try:
                PythonActivity.mActivity.unregisterActivityResultListener(
                    self.android_intent_handler
                )
                print("DEBUG: android_intent_handler removed.")
            except Exception as e:
                print(f"ERROR: Could not remove android_intent_handler: {e}")
            finally:
                self.android_intent_handler = (
                    None  # Đặt lại để chuẩn bị cho lần chọn tiếp theo
                )

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
                        display_name_column_index = cursor.getColumnIndex(
                            autoclass("android.provider.OpenableColumns").DISPLAY_NAME
                        )
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
            # TODO: Lưu URI này vào config file hoặc lưu trữ cục bộ để có thể truy cập lại sau này

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

                        with content_resolver.openInputStream(
                            child_document.getUri()
                        ) as input_stream:
                            with open(dest_file_path, "wb") as output_stream:
                                buffer = bytearray(4096)
                                bytes_read = input_stream.read(buffer)
                                while bytes_read != -1:
                                    if bytes_read > 0:
                                        output_stream.write(buffer[:bytes_read])
                                    bytes_read = input_stream.read(buffer)
                        print(
                            f"DEBUG: Đã sao chép tệp '{file_name}' vào '{dest_file_path}'"
                        )
                    except Exception as e:
                        print(f"Lỗi khi sao chép tệp '{file_name}': {e}")
                else:
                    print(f"DEBUG: Bỏ qua tệp không hợp lệ: {file_name}")

    def get_book_list(self):
        book_list = []
        if not os.path.exists(self.book_folder_path):
            os.makedirs(self.book_folder_path, exist_ok=True)  # Dùng exist_ok=True luôn
            print(
                f"DEBUG (BookManager): Thư mục '{self.book_folder_path}' không tồn tại, đã tạo."
            )
            return []

        files_in_folder = os.listdir(self.book_folder_path)
        print(
            f"DEBUG (BookManager): Các file được tìm thấy trong '{self.book_folder_path}': {files_in_folder}"
        )

        for filename in files_in_folder:
            for ext in SUPPORTED_EXTENSIONS:  # SỬ DỤNG SUPPORTED_EXTENSIONS TOÀN CỤC
                if filename.lower().endswith(
                    ext
                ):  # Đảm bảo so sánh không phân biệt chữ hoa/thường
                    book_name = os.path.splitext(filename)[0].replace("_", " ").title()
                    book_list.append((book_name, filename))
                    break  # Tìm thấy extension hợp lệ, thoát vòng lặp ext
        return book_list

    def read_book_content(self, book_filename):
        """
        Đọc nội dung của một file sách dựa trên định dạng.
        Trả về book_data và chapter_list, cùng với error_type (None nếu không có lỗi).
        """
        full_path = os.path.join(self.book_folder_path, book_filename)
        book_data = []
        chapter_list = []
        book_name = os.path.splitext(book_filename)[0].replace("_", " ").title()

        if not os.path.exists(full_path):
            print(f"DEBUG (BookManager): File sách không tìm thấy: {full_path}")
            return [], [], "file_not_found"

        try:
            if book_filename.lower().endswith(".txt"):
                book_data, chapter_list = read_book_txt(full_path)
                print(
                    f"DEBUG (BookManager): Sách TXT '{book_name}' đã được đọc từ '{full_path}'."
                )
            elif book_filename.lower().endswith(".html"):
                book_data, chapter_list = read_book_html(full_path)
                print(
                    f"DEBUG (BookManager): Sách HTML '{book_name}' đã được đọc từ '{full_path}'."
                )
            else:
                print(
                    f"DEBUG (BookManager): Định dạng file không được hỗ trợ: {book_filename}"
                )
                return [], [], "unsupported_format"
        except Exception as e:
            print(f"DEBUG (BookManager): Lỗi khi đọc nội dung sách '{full_path}': {e}")
            return [], [], "read_error"

        if (
            not book_data and not chapter_list
        ):  # Kiểm tra cả hai để chắc chắn là có nội dung
            print(
                f"DEBUG (BookManager): Không có dữ liệu sách sau khi đọc từ '{full_path}'."
            )
            return [], [], "read_error"

        return book_data, chapter_list, None
