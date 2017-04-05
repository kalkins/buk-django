function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function() {
    $(".editable-content").each(function() {
        var skin = "charcoal";
        if ($(".side:nth-child(2n)").find($(this)).length == 0) {
            skin = "lightgray";
        }
        var $editor = $(this);

        tinymce.init({
            selector: "#"+$(this).attr("id"),
            skin: skin,
            plugins: "link image imagetools",
            file_browser_callback_types: "image",
            file_browser_callback: function(field_name, url, type, win) {
                var $input = $("<input type='file' style='display: none;' />")
                    .insertAfter($editor);
                $input.change(function(event) {
                    win.document.getElementById(field_name).value = URL.createObjectURL(event.target.files[0]);
                });
                $input.trigger("click");
            },
            language: "nb_NO",
            inline: true,
            menu: {
                edit: {title: 'Edit', items: 'undo redo | cut copy paste pastetext | selectall'},
                insert: {title: 'Insert', items: 'link media | template hr'},
                format: {title: 'Format', items: 'bold italic underline strikethrough superscript subscript | formats | removeformat'},
            },
            toolbar: "undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | save | done",
            setup: function(editor) {
                var locked = true;
                var $editor = $("#"+editor.id);

                editor.setMode("readonly");
                
                $editor.dblclick(function() {
                    if (locked) {
                        if (window.getSelection) {
                            window.getSelection().removeAllRanges();
                        } else if (document.selection) {
                            document.selection.empty();
                        }
                        editor.setMode("design");
                        editor.fire("activate");
                        $editor.find("a").off("click");
                        locked = false;
                    }
                });

                editor.addButton("save", {
                    text: "Lagre",
                    disabled: true,
                    onclick: function() {
                        editor.setProgressState(true);
                        var btn = this;
                        var navn = $(editor.getElement()).data("name");
                        var num_uploads = 0;
                        var uploads_completed = 0;
                        var error = false;

                        function uploadContents() {
                            if (!error && num_uploads == uploads_completed) {
                                // As .getContent() returnes a set of all the child elements of the
                                // editor we must append it to a dummy element to get the html content
                                var $content = $('<div />').append($(editor.getContent()).clone());
                                // Go through the images in the editor to get the correct sizes
                                $editor.find("img").each(function(i) {
                                    // Convert the image size to make it consistent across all screens
                                    // The width is stored as a percentage, so that it's tied to the width
                                    // of the screen. The height is stored as a percentage of the height,
                                    // which is applied through padding, to keep the aspect ratio.
                                    var min_width = "";
                                    // Set a minimum width, so that images doesn't shrink too much on small screens.
                                    // The standard minimum width is overridden if the image is originally smaller than that
                                    if ($(this).width() < 100) {
                                        min_width = $(this).width() + "px";
                                    } else {
                                        min_width = "100px";
                                    }
                                    var width = (100 * $(this).width() / $editor.width()) + "%";
                                    var padding = ($(this).height() / $(this).width()) + "%";

                                    // Set the size of the cloned images
                                    $content.find("img").eq(i).css("width", width).css("padding-bottom", padding)
                                            .css("min-width", min_width).css("max-width", "100%")
                                            .removeAttr("height").removeAttr("width");
                                });
                                var content = $content.html();

                                $.ajax("/endre-innhold/", {
                                    method: "POST",
                                    dataType: "JSON",
                                    data: {name: navn, content: content},
                                    headers: {"X-CSRFToken": getCookie("csrftoken")},
                                    success: function(data) {
                                        if (typeof data["success"] == "undefined" || !data["success"]) {
                                            error = true;
                                            if (typeof data["error"] == "undefined") {
                                                alert("Det har oppstått en feil. Ta kontakt med webkom.");
                                            } else {
                                                alert(data["error"]);
                                            }
                                        } else {
                                            btn.disabled(true);
                                        }
                                    },
                                    complete: function() {
                                        editor.setProgressState(false);
                                    }
                                });
                            }
                        }

                        $editor.find("img").each(function(i) {
                            var $img = $(this);
                            var src = $img.attr("src");
                            if (!error && src.startsWith("blob")) {
                                num_uploads += 1;
                                var xhr = new XMLHttpRequest();
                                xhr.open('GET', src, true);
                                xhr.responseType = 'blob';

                                xhr.onload = function(e) {
                                    if (this.status == 200) {
                                        var blob = this.response;
                                        var xhr, formData;

                                        xhr = new XMLHttpRequest();
                                        xhr.withCredentials = false;
                                        xhr.open('POST', '/endre-innhold/bilde');

                                        xhr.onload = function() {
                                            if (error) {
                                                return;
                                            }
                                            var json;

                                            if (xhr.status != 200) {
                                                error = true;
                                                console.log('HTTP Error: ' + xhr.status);
                                                alert("Det har oppstått en feil. Ta kontakt med webkom.");
                                                return;
                                            }

                                            json = JSON.parse(xhr.responseText);

                                            if (!json || typeof json.location != 'string') {
                                                editor.setProgressState(false);
                                                error = true;
                                                if (json.hasOwnProperty("error")) {
                                                    alert(json.error);
                                                } else {
                                                    alert("Det har oppstått en feil. Ta kontakt med webkom.");
                                                }
                                                return;
                                            }

                                            $img.attr("src", json.location);
                                            uploads_completed += 1;
                                            uploadContents();
                                        };

                                        formData = new FormData();
                                        formData.append('navn', navn);
                                        var blobname = "blob" + i;
                                        formData.append('blobname', blobname);
                                        formData.append(blobname, blob);

                                        xhr.send(formData);
                                    }
                                };

                                xhr.send();
                            }
                        }).promise().done(function() {
                            uploadContents();
                        });
                    },
                    onpostrender: function() {
                        var btn = this;
                        editor.on("change", function(e) {
                            btn.disabled(false);
                        });
                    }
                });

                editor.addButton("done", {
                    text: "Ferdig",
                    onclick: function() {
                        editor.setMode("readonly");
                        editor.fire("deactivate");
                        $editor.find("a").click(function(event) {
                            event.stopPropagation();
                        });
                        locked = true;
                    }
                });
            }
        }).then(function(editors) {
            // This is executed when the editor is initialized
            for (var i = 0; i < editors.length; i++) {
                var editor = editors[i];

                // Make links clickable as the editor is disabled to begin with
                var $editor = $("#"+editor.id);
                $editor.find("a").click(function(event) {
                    event.stopPropagation();
                });
            }
        });
    });
});
