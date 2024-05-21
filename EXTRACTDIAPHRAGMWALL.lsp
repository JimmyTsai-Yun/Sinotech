;------------------------------------------LOOP EVERY FILES------------------------------------------
(defun wtype_selection ( / wtype)
  (setq option '("Diaphragm" "SheetPile"))
  (setq dcl_id (load_dialog "dcl\\dtype_selection.dcl"))
  (if (not (new_dialog "dtype_selection" dcl_id)) (exit))
  (start_list "selections")
  (mapcar 'add_list option)
  (end_list)
  (action_tile "accept"
  (strcat
  "(progn"
  "(setq selected_option (atof (get_tile \"selections\")))"
  "(done_dialog) (setq userclick T))"
  ))
  (action_tile "cancel"
  (strcat
  "(quit)"
  ))
  (start_dialog)
  (unload_dialog dcl_id)
  (setq selected_option (fix selected_option))
  (setq selected_option (nth selected_option option))
  (setq wtype selected_option)
)

(defun dtype_selection ( / dtype)
  (setq option '("Plan Drawings" "Elevation Drawings" "Structural Descriptions" "Rebar Drawings"))
  (setq dcl_id (load_dialog "dcl\\dtype_selection.dcl"))
  (if (not (new_dialog "dtype_selection" dcl_id)) (exit))
  (start_list "selections")
  (mapcar 'add_list option)
  (end_list)
  (action_tile "accept"
  (strcat
  "(progn"
  "(setq selected_option (atof (get_tile \"selections\")))"
  "(done_dialog) (setq userclick T))"
  ))
  (action_tile "cancel"
  (strcat
  "(quit)"
  ))
  (start_dialog)
  (unload_dialog dcl_id)
  (setq selected_option (fix selected_option))
  (setq selected_option (nth selected_option option))
  (setq dtype selected_option)
)

(defun preloop_for_selectlayer_folder (dirpath dwgname_list)
  (setq collectedlayer '())
  (setq collectedlayer_file '())
  (setq dwgname_list_shown dwgname_list)
  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (setq layouts (vla-get-Layouts doc))
    (setq exportable  "False")
    (vlax-for layout layouts
      (if (vl-string-search "1" (vla-get-Name layout))
        (progn
        (setq *layoutname_list* (append *layoutname_list* (list (vla-get-Name layout))))
        (set-layout-plotter-config doc (vla-get-Name layout) "AutoCAD PDF (General Documentation).pc3")
        (setq exportable  "True")
        )
      )
    )
    (if (equal exportable "False")
    (progn
      (princ (strcat "Layout1 / 配置1 is not found in " (car dwgname_list) ", there will be problem exporting the pdf"))
      (setq *layoutname_list* (/ 1 0))
    )
    )
    (vla-StartUndoMark doc) 
    (setq tempcollectedlayer '())
    (vlax-for layer (vla-get-layers doc)
        (setq tempcollectedlayer (cons (vla-get-name layer) tempcollectedlayer))
    )
    (setq tempcollectedlayer (reverse tempcollectedlayer))
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq collectedlayer_file (append collectedlayer_file (list dwgname )))
    (setq collectedlayer (append collectedlayer (list tempcollectedlayer)))
    (setq dwgname_list (cdr dwgname_list))
  )

  (setq collectedlayer_wall collectedlayer)
  (setq collectedlayer_text collectedlayer)
  (setq dcl_id (load_dialog "dcl\\layer_selection.dcl")) ; change directory path to known location
  (if (not (new_dialog "layer_selection" dcl_id))
  (exit)
  )
    
  (start_list "source_wall")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list)
  (action_tile "source_wall" 
    (vl-prin1-to-string
      '(progn
        (setq selected_index (atoi (get_tile "source_wall")))
        (start_list "all_wall")
        (foreach itm (nth selected_index collectedlayer_wall) (add_list itm))
        (end_list)
        (set_tile "all_wall" "0")
        (set_tile "all_wall_slider" "0")
      )
    )
  )

  (start_list "source_text")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list) 
  (action_tile "source_text" 
    (vl-prin1-to-string
      '(progn
        (setq selected_index (atoi (get_tile "source_text")))
        (start_list "all_text")
        (foreach itm (nth selected_index collectedlayer_text) (add_list itm))
        (end_list)
        (set_tile "all_text" "0")
        (set_tile "all_text_slider" "0")
      )
    )
  )

  (start_list "all_wall")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "all_wall" "")
  
  (start_list "all_text")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "all_text" "")
  
  (action_tile "selected_wall_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_wall_file")))
        (start_list "selected_wall")
        (foreach itm (nth added_index wall_layer) (add_list itm))
        (end_list)
        (set_tile "selected_wall_slider" "0")
      )
    )
  )
  
  (action_tile "selected_text_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_text_file")))
        (start_list "selected_text")
        (foreach itm (nth added_index text_layer) (add_list itm))
        (end_list)
        (set_tile "selected_text_slider" "0")
        )
    )
  )
  
  (action_tile "add_wall"
      (vl-prin1-to-string
        '(progn
          (setq selected_index (atoi (get_tile "source_wall")))
          (setq sel_filename (nth selected_index dwgname_list_shown))
          (if (boundp 'wall_file)
            (progn
               (if (not (member sel_filename wall_file))
                (progn
                 (setq wall_file (append wall_file (list sel_filename)))
                 (setq wall_layer (append wall_layer (list'())))
                )
               )
            )
            (progn
               (setq wall_file (list sel_filename))
               (setq wall_layer (list'()))
            ))
          (start_list "selected_wall_file")
            (foreach itm wall_file (add_list itm))
          (end_list)
          (setq added_index (vl-position sel_filename wall_file))
          (set_tile "selected_wall_file" (vl-princ-to-string added_index))
          
          (setq temp_collectedlayer_wall  (nth selected_index collectedlayer_wall))
          (setq temp_wall_layer  (nth added_index wall_layer))
          (mapcar 'dclist '("all_wall" "selected_wall")
              (mapcar 'set '(temp_collectedlayer_wall temp_wall_layer)
                  (shiftitems (read (strcat "(" (get_tile "all_wall") ")")) temp_collectedlayer_wall temp_wall_layer)
              ))
          (set_tile "all_wall_slider" "0")
          (set_tile "selected_wall_file_slider" "0")
          (set_tile "selected_wall_slider" "0")
          (setq collectedlayer_wall (SubstNth temp_collectedlayer_wall selected_index collectedlayer_wall))
          (setq wall_layer (SubstNth temp_wall_layer added_index wall_layer))
          )))
  (action_tile "remove_wall"
      (vl-prin1-to-string
          '(progn
            (setq added_index (atoi (get_tile "selected_wall_file")))
            (setq sel_filename (nth added_index wall_file))
            (setq selected_index (vl-position sel_filename dwgname_list_shown))
            (setq temp_collectedlayer_wall  (nth selected_index collectedlayer_wall))
            (setq temp_wall_layer  (nth added_index wall_layer))
            (mapcar 'dclist '("selected_wall" "all_wall")
              (mapcar 'set '(temp_wall_layer temp_collectedlayer_wall)
                  (shiftitems  (read (strcat "(" (get_tile "selected_wall") ")")) temp_wall_layer temp_collectedlayer_wall)
              ))
            (setq collectedlayer_wall (SubstNth temp_collectedlayer_wall selected_index collectedlayer_wall))
            (setq wall_layer (SubstNth temp_wall_layer added_index wall_layer))
            
            (set_tile "source_wall" (itoa (vl-position sel_filename dwgname_list_shown)))
            (set_tile "all_wall_slider" "0")
            (set_tile "selected_wall_slider" "0")
            
            (if (null temp_wall_layer)
              (progn
                (setq wall_file (RemoveNth added_index wall_file))
                (setq wall_layer (RemoveNth added_index wall_layer))
                (start_list "selected_wall_file")
                (foreach itm wall_file (add_list itm))
                (end_list)
                (set_tile "selected_wall_file_slider" "0")
              ))
            )))

  (action_tile "add_text"
      (vl-prin1-to-string
        '(progn
          (setq selected_index (atoi (get_tile "source_text")))
          (setq sel_filename (nth selected_index dwgname_list_shown))
          (if (boundp 'text_file)
            (progn
               (if (not (member sel_filename text_file))
                (progn
                 (setq text_file (append text_file (list sel_filename)))
                 (setq text_layer (append text_layer (list'())))
                )
               )
            )
            (progn
               (setq text_file (list sel_filename))
               (setq text_layer (list'()))
            ))
          (start_list "selected_text_file")
            (foreach itm text_file (add_list itm))
          (end_list)
          (setq added_index (vl-position sel_filename text_file))
          (set_tile "selected_text_file" (vl-princ-to-string added_index))
          
          (setq temp_collectedlayer_text  (nth selected_index collectedlayer_text))
          (setq temp_text_layer  (nth added_index text_layer))
          (mapcar 'dclist '("all_text" "selected_text")
              (mapcar 'set '(temp_collectedlayer_text temp_text_layer)
                  (shiftitems (read (strcat "(" (get_tile "all_text") ")")) temp_collectedlayer_text temp_text_layer)
              ))
          (set_tile "all_text_slider" "0")
          (set_tile "selected_text_file_slider" "0")
          (set_tile "selected_text_slider" "0")
          (setq collectedlayer_text (SubstNth temp_collectedlayer_text selected_index collectedlayer_text))
          (setq text_layer (SubstNth temp_text_layer added_index text_layer))
          )))
  (action_tile "remove_text"
      (vl-prin1-to-string
          '(progn
            (setq added_index (atoi (get_tile "selected_text_file")))
            (setq sel_filename (nth added_index text_file))
            (setq selected_index (vl-position sel_filename dwgname_list_shown))
            (setq temp_collectedlayer_text  (nth selected_index collectedlayer_text))
            (setq temp_text_layer  (nth added_index text_layer))
            (mapcar 'dclist '("selected_text" "all_text")
              (mapcar 'set '(temp_text_layer temp_collectedlayer_text)
                  (shiftitems  (read (strcat "(" (get_tile "selected_text") ")")) temp_text_layer temp_collectedlayer_text)
              ))
            (setq collectedlayer_text (SubstNth temp_collectedlayer_text selected_index collectedlayer_text))
            (setq text_layer (SubstNth temp_text_layer added_index text_layer))
            
            (set_tile "source_text" (itoa (vl-position sel_filename dwgname_list_shown)))
            (set_tile "all_text_slider" "0")
            (set_tile "selected_text_slider" "0")
            
            (if (null temp_text_layer)
              (progn
                (setq text_file (RemoveNth added_index text_file))
                (setq text_layer (RemoveNth added_index text_layer))
                (start_list "selected_text_file")
                (foreach itm text_file (add_list itm))
                (end_list)
                (set_tile "selected_text_file_slider" "0")
              )) 
            )))
  
  (action_tile "source_wall_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_wall_slider" "source_wall" dwgname_list_shown 3 "   ")))
  (action_tile "all_wall_slider" (vl-prin1-to-string '(slider_cut_restore_string "all_wall_slider" "all_wall" (nth (atoi (get_tile "source_wall")) collectedlayer_wall) 3 "   ")))
  (action_tile "selected_wall_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_wall_file_slider" "selected_wall_file" wall_file 3 "   ")))
  (action_tile "selected_wall_slider" (vl-prin1-to-string '(if (not (equal wall_file nil))
      (slider_cut_restore_string "selected_wall_slider" "selected_wall" (nth (atoi (get_tile "selected_wall_file")) wall_layer) 3 "   "))
      ))
  
  (action_tile "source_text_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_text_slider" "source_text" dwgname_list_shown 3 "   ")))
  (action_tile "all_text_slider" (vl-prin1-to-string '(slider_cut_restore_string "all_text_slider" "all_text" (nth (atoi (get_tile "source_text")) collectedlayer_text) 3 "   ")))
  (action_tile "selected_text_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_text_file_slider" "selected_text_file" text_file 3 "   ")))
  (action_tile "selected_text_slider" (vl-prin1-to-string '(if (not (equal text_file nil))
      (slider_cut_restore_string "selected_text_slider" "selected_text" (nth (atoi (get_tile "selected_text_file")) text_layer) 3 "   "))
      ))
  
  (action_tile "accept"
  (vl-prin1-to-string
          '(progn
            (if (and
              (equal (vl-sort wall_file '<) (vl-sort text_file '<))
              (equal (vl-sort text_file '<) (vl-sort wall_file '<))
            )
          (done_dialog)
          (alert "Please make sure the Selected File(s) are all the same !"))
  )))
  
  (action_tile "cancel"
  (strcat
  "(quit)"
  ))
  (start_dialog)
  (unload_dialog dcl_id)
  (setq target_layer (list wall_file text_file wall_layer text_layer))

)

(defun preloopp_for_all_folder (dirpath dwgname_list)
  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (setq layouts (vla-get-Layouts doc))
    (setq exportable  "False")
    (vlax-for layout layouts
      (if (vl-string-search "1" (vla-get-Name layout))
        (progn
        (setq *layoutname_list* (append *layoutname_list* (list (vla-get-Name layout))))
        (set-layout-plotter-config doc (vla-get-Name layout) "AutoCAD PDF (General Documentation).pc3")
        (setq exportable  "True")
        )
      )
    )
    (if (equal exportable "False")
    (progn
      (princ (strcat "Layout1 / 配置1 is not found in " (car dwgname_list) ", there will be problem exporting the pdf"))
      (setq *layoutname_list* (/ 1 0))
    )
    )
    (vla-StartUndoMark doc) 
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq dwgname_list (cdr dwgname_list))
  )
)

(defun preloop (dirpath dwgname_list / text_file wall_file text_layer wall_layer)
  (setq collectedlayer '())
  (setq collectedlayer_file '())
  (setq dwgname_list_shown dwgname_list)
  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (setq layouts (vla-get-Layouts doc))
    (setq exportable  "False")
    (vlax-for layout layouts
      (if (vl-string-search "1" (vla-get-Name layout))
        (progn
        (setq *layoutname_list* (append *layoutname_list* (list (vla-get-Name layout))))
        (set-layout-plotter-config doc (vla-get-Name layout) "AutoCAD PDF (General Documentation).pc3")
        (setq exportable  "True")
        )
      )
    )
    (if (equal exportable "False")
    (progn
      (princ (strcat "Layout1 / 配置1 is not found in " (car dwgname_list) ", there will be problem exporting the pdf"))
      (setq *layoutname_list* (/ 1 0))
    )
    )
    (vla-StartUndoMark doc) 
    (setq tempcollectedlayer '())
    (vlax-for layer (vla-get-layers doc)
        (setq tempcollectedlayer (cons (vla-get-name layer) tempcollectedlayer))
    )
    (setq tempcollectedlayer (reverse tempcollectedlayer))
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq collectedlayer_file (append collectedlayer_file (list dwgname )))
    (setq collectedlayer (append collectedlayer (list tempcollectedlayer)))
    (setq dwgname_list (cdr dwgname_list))
  )
  (setq collectedlayer_wall collectedlayer)
  (setq collectedlayer_text collectedlayer)
  (setq dcl_id (load_dialog "dcl\\layer_selection.dcl")) ; change directory path to known location
  (if (not (new_dialog "layer_selection" dcl_id))
  (exit)
  )
    
  (start_list "source_wall")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list)
  (action_tile "source_wall" 
    (vl-prin1-to-string
      '(progn
        (setq selected_index (atoi (get_tile "source_wall")))
        (start_list "all_wall")
        (foreach itm (nth selected_index collectedlayer_wall) (add_list itm))
        (end_list)
        (set_tile "all_wall" "0")
        (set_tile "all_wall_slider" "0")
      )
    )
  )

  (start_list "source_text")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list) 
  (action_tile "source_text" 
    (vl-prin1-to-string
      '(progn
        (setq selected_index (atoi (get_tile "source_text")))
        (start_list "all_text")
        (foreach itm (nth selected_index collectedlayer_text) (add_list itm))
        (end_list)
        (set_tile "all_text" "0")
        (set_tile "all_text_slider" "0")
      )
    )
  )

  (start_list "all_wall")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "all_wall" "")
  
  (start_list "all_text")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "all_text" "")
  
  (action_tile "selected_wall_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_wall_file")))
        (start_list "selected_wall")
        (foreach itm (nth added_index wall_layer) (add_list itm))
        (end_list)
        (set_tile "selected_wall_slider" "0")
      )
    )
  )
  
  (action_tile "selected_text_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_text_file")))
        (start_list "selected_text")
        (foreach itm (nth added_index text_layer) (add_list itm))
        (end_list)
        (set_tile "selected_text_slider" "0")
        )
    )
  )
  
  (action_tile "add_wall"
      (vl-prin1-to-string
        '(progn
          (setq selected_index (atoi (get_tile "source_wall")))
          (setq sel_filename (nth selected_index dwgname_list_shown))
          (if (boundp 'wall_file)
            (progn
               (if (not (member sel_filename wall_file))
                (progn
                 (setq wall_file (append wall_file (list sel_filename)))
                 (setq wall_layer (append wall_layer (list'())))
                )
               )
            )
            (progn
               (setq wall_file (list sel_filename))
               (setq wall_layer (list'()))
            ))
          (start_list "selected_wall_file")
            (foreach itm wall_file (add_list itm))
          (end_list)
          (setq added_index (vl-position sel_filename wall_file))
          (set_tile "selected_wall_file" (vl-princ-to-string added_index))
          
          (setq temp_collectedlayer_wall  (nth selected_index collectedlayer_wall))
          (setq temp_wall_layer  (nth added_index wall_layer))
          (mapcar 'dclist '("all_wall" "selected_wall")
              (mapcar 'set '(temp_collectedlayer_wall temp_wall_layer)
                  (shiftitems (read (strcat "(" (get_tile "all_wall") ")")) temp_collectedlayer_wall temp_wall_layer)
              ))
          (set_tile "all_wall_slider" "0")
          (set_tile "selected_wall_file_slider" "0")
          (set_tile "selected_wall_slider" "0")
          (setq collectedlayer_wall (SubstNth temp_collectedlayer_wall selected_index collectedlayer_wall))
          (setq wall_layer (SubstNth temp_wall_layer added_index wall_layer))
          )))
  (action_tile "remove_wall"
      (vl-prin1-to-string
          '(progn
            (setq added_index (atoi (get_tile "selected_wall_file")))
            (setq sel_filename (nth added_index wall_file))
            (setq selected_index (vl-position sel_filename dwgname_list_shown))
            (setq temp_collectedlayer_wall  (nth selected_index collectedlayer_wall))
            (setq temp_wall_layer  (nth added_index wall_layer))
            (mapcar 'dclist '("selected_wall" "all_wall")
              (mapcar 'set '(temp_wall_layer temp_collectedlayer_wall)
                  (shiftitems  (read (strcat "(" (get_tile "selected_wall") ")")) temp_wall_layer temp_collectedlayer_wall)
              ))
            (setq collectedlayer_wall (SubstNth temp_collectedlayer_wall selected_index collectedlayer_wall))
            (setq wall_layer (SubstNth temp_wall_layer added_index wall_layer))
            
            (set_tile "source_wall" (itoa (vl-position sel_filename dwgname_list_shown)))
            (set_tile "all_wall_slider" "0")
            (set_tile "selected_wall_slider" "0")
            
            (if (null temp_wall_layer)
              (progn
                (setq wall_file (RemoveNth added_index wall_file))
                (setq wall_layer (RemoveNth added_index wall_layer))
                (start_list "selected_wall_file")
                (foreach itm wall_file (add_list itm))
                (end_list)
                (set_tile "selected_wall_file_slider" "0")
              ))
            )))

  (action_tile "add_text"
      (vl-prin1-to-string
        '(progn
          (setq selected_index (atoi (get_tile "source_text")))
          (setq sel_filename (nth selected_index dwgname_list_shown))
          (if (boundp 'text_file)
            (progn
               (if (not (member sel_filename text_file))
                (progn
                 (setq text_file (append text_file (list sel_filename)))
                 (setq text_layer (append text_layer (list'())))
                )
               )
            )
            (progn
               (setq text_file (list sel_filename))
               (setq text_layer (list'()))
            ))
          (start_list "selected_text_file")
            (foreach itm text_file (add_list itm))
          (end_list)
          (setq added_index (vl-position sel_filename text_file))
          (set_tile "selected_text_file" (vl-princ-to-string added_index))
          
          (setq temp_collectedlayer_text  (nth selected_index collectedlayer_text))
          (setq temp_text_layer  (nth added_index text_layer))
          (mapcar 'dclist '("all_text" "selected_text")
              (mapcar 'set '(temp_collectedlayer_text temp_text_layer)
                  (shiftitems (read (strcat "(" (get_tile "all_text") ")")) temp_collectedlayer_text temp_text_layer)
              ))
          (set_tile "all_text_slider" "0")
          (set_tile "selected_text_file_slider" "0")
          (set_tile "selected_text_slider" "0")
          (setq collectedlayer_text (SubstNth temp_collectedlayer_text selected_index collectedlayer_text))
          (setq text_layer (SubstNth temp_text_layer added_index text_layer))
          )))
  (action_tile "remove_text"
      (vl-prin1-to-string
          '(progn
            (setq added_index (atoi (get_tile "selected_text_file")))
            (setq sel_filename (nth added_index text_file))
            (setq selected_index (vl-position sel_filename dwgname_list_shown))
            (setq temp_collectedlayer_text  (nth selected_index collectedlayer_text))
            (setq temp_text_layer  (nth added_index text_layer))
            (mapcar 'dclist '("selected_text" "all_text")
              (mapcar 'set '(temp_text_layer temp_collectedlayer_text)
                  (shiftitems  (read (strcat "(" (get_tile "selected_text") ")")) temp_text_layer temp_collectedlayer_text)
              ))
            (setq collectedlayer_text (SubstNth temp_collectedlayer_text selected_index collectedlayer_text))
            (setq text_layer (SubstNth temp_text_layer added_index text_layer))
            
            (set_tile "source_text" (itoa (vl-position sel_filename dwgname_list_shown)))
            (set_tile "all_text_slider" "0")
            (set_tile "selected_text_slider" "0")
            
            (if (null temp_text_layer)
              (progn
                (setq text_file (RemoveNth added_index text_file))
                (setq text_layer (RemoveNth added_index text_layer))
                (start_list "selected_text_file")
                (foreach itm text_file (add_list itm))
                (end_list)
                (set_tile "selected_text_file_slider" "0")
              )) 
            )))
  
  (action_tile "source_wall_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_wall_slider" "source_wall" dwgname_list_shown 3 "   ")))
  (action_tile "all_wall_slider" (vl-prin1-to-string '(slider_cut_restore_string "all_wall_slider" "all_wall" (nth (atoi (get_tile "source_wall")) collectedlayer_wall) 3 "   ")))
  (action_tile "selected_wall_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_wall_file_slider" "selected_wall_file" wall_file 3 "   ")))
  (action_tile "selected_wall_slider" (vl-prin1-to-string '(if (not (equal wall_file nil))
      (slider_cut_restore_string "selected_wall_slider" "selected_wall" (nth (atoi (get_tile "selected_wall_file")) wall_layer) 3 "   "))
      ))
  
  (action_tile "source_text_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_text_slider" "source_text" dwgname_list_shown 3 "   ")))
  (action_tile "all_text_slider" (vl-prin1-to-string '(slider_cut_restore_string "all_text_slider" "all_text" (nth (atoi (get_tile "source_text")) collectedlayer_text) 3 "   ")))
  (action_tile "selected_text_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_text_file_slider" "selected_text_file" text_file 3 "   ")))
  (action_tile "selected_text_slider" (vl-prin1-to-string '(if (not (equal text_file nil))
      (slider_cut_restore_string "selected_text_slider" "selected_text" (nth (atoi (get_tile "selected_text_file")) text_layer) 3 "   "))
      ))
  
  (action_tile "accept"
  (vl-prin1-to-string
          '(progn
            (if (and
              (equal (vl-sort wall_file '<) (vl-sort text_file '<))
              (equal (vl-sort text_file '<) (vl-sort wall_file '<))
            )
          (done_dialog)
          (alert "Please make sure the Selected File(s) are all the same !"))
  )))
  
  (action_tile "cancel"
  (strcat
  "(quit)"
  ))
  (start_dialog)
  (unload_dialog dcl_id)
  (setq target_layer (list wall_file text_file wall_layer text_layer))
)

(defun preloop4 (dirpath dwgname_list / text_file wall_file pointer_file text_layer wall_layer pointer_layer text_file_2 wall_file_2 pointer_file_2 text_layer_2 wall_layer_2 pointer_layer_2)
  (setq collectedlayer '())
  (setq collectedlayer_file '())
  (setq collectedblock '())
  (setq dwgname_list_shown dwgname_list)
  (while dwgname_list
    (setq tempcollectedlayer '())
    (setq tempcollectedblock '())
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (setq layouts (vla-get-Layouts doc))
    (setq exportable  "False")
    (vlax-for layout layouts
      (if (vl-string-search "1" (vla-get-Name layout))
        (progn
        (setq *layoutname_list* (append *layoutname_list* (list (vla-get-Name layout))))
        (set-layout-plotter-config doc (vla-get-Name layout) "AutoCAD PDF (General Documentation).pc3")
        (setq exportable  "True")
        )
      )
    )
    (if (equal exportable "False")
    (progn
      (princ (strcat "Layout1 / 配置1 is not found in " (car dwgname_list) ", there will be problem exporting the pdf"))
      (setq *layoutname_list* (/ 1 0))
    )
    )
    (vla-StartUndoMark doc)
    
    (vlax-for layer (vla-get-layers doc)
        (setq tempcollectedlayer (cons (vla-get-name layer) tempcollectedlayer))
    )
    (setq tempcollectedlayer (reverse tempcollectedlayer))
    
    (vlax-for blk (vla-get-blocks doc)
        (setq tempcollectedblock (cons (vla-get-name blk) tempcollectedblock))
    )
    
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq collectedlayer_file (append collectedlayer_file (list dwgname )))
    (setq collectedlayer (append collectedlayer (list tempcollectedlayer)))
    (setq collectedblock (append collectedblock (list tempcollectedblock)))
    (setq dwgname_list (cdr dwgname_list))
  )
  (setq collectedlayer_wall collectedlayer)
  (setq collectedlayer_text collectedlayer)
  (setq collectedlayer_pointer collectedlayer)
  (setq collectedlayer_wall_2 collectedlayer)
  (setq collectedlayer_text_2 collectedlayer)
  (setq collectedlayer_pointer_2 collectedblock)
  (setq dcl_id (load_dialog "dcl\\vert_rebar_layer_selection.dcl")) ; change directory path to known location
  (if (not (new_dialog "layer_selection" dcl_id))
  (exit)
  )
    
  (start_list "source_wall")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list)
  (action_tile "source_wall" 
    (vl-prin1-to-string
      '(progn
        (setq selected_index (atoi (get_tile "source_wall")))
        (start_list "all_wall")
        (foreach itm (nth selected_index collectedlayer_wall) (add_list itm))
        (end_list)
        (set_tile "all_wall" "0")
        (set_tile "all_wall_slider" "0")
      )
    )
  )

  (start_list "source_text")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list) 
  (action_tile "source_text" 
    (vl-prin1-to-string
      '(progn
        (setq selected_index (atoi (get_tile "source_text")))
        (start_list "all_text")
        (foreach itm (nth selected_index collectedlayer_text) (add_list itm))
        (end_list)
        (set_tile "all_text" "0")
        (set_tile "all_text_slider" "0")
      )
    )
  )

  (start_list "source_pointer")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list) 
  (action_tile "source_pointer" 
    (vl-prin1-to-string
      '(progn
        (setq selected_index (atoi (get_tile "source_pointer")))
        (start_list "all_pointer")
        (foreach itm (nth selected_index collectedlayer_pointer) (add_list itm))
        (end_list)
        (set_tile "all_pointer" "0")
        (set_tile "all_pointer_slider" "0")
      )
    )
  )
  
  (start_list "all_wall")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "all_wall" "")
  
  (start_list "all_text")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "all_text" "")
  
  (start_list "all_pointer")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "all_pointer" "")
  
  (action_tile "selected_wall_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_wall_file")))
        (start_list "selected_wall")
        (foreach itm (nth added_index wall_layer) (add_list itm))
        (end_list)
        (set_tile "selected_wall_slider" "0")
      )
    )
  )
  
  (action_tile "selected_text_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_text_file")))
        (start_list "selected_text")
        (foreach itm (nth added_index text_layer) (add_list itm))
        (end_list)
        (set_tile "selected_text_slider" "0")
        )
    )
  )
  
  (action_tile "selected_pointer_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_pointer_file")))
        (start_list "selected_pointer")
        (foreach itm (nth added_index pointer_layer) (add_list itm))
        (end_list)
        (set_tile "selected_pointer_slider" "0")
        )
    )
  )
  
  (action_tile "add_wall"
      (vl-prin1-to-string
        '(progn
          (setq selected_index (atoi (get_tile "source_wall")))
          (setq sel_filename (nth selected_index dwgname_list_shown))
          (if (boundp 'wall_file)
            (progn
               (if (not (member sel_filename wall_file))
                (progn
                 (setq wall_file (append wall_file (list sel_filename)))
                 (setq wall_layer (append wall_layer (list'())))
                )
               )
            )
            (progn
               (setq wall_file (list sel_filename))
               (setq wall_layer (list'()))
            ))
          (start_list "selected_wall_file")
            (foreach itm wall_file (add_list itm))
          (end_list)
          (setq added_index (vl-position sel_filename wall_file))
          (set_tile "selected_wall_file" (vl-princ-to-string added_index))
          
          (setq temp_collectedlayer_wall  (nth selected_index collectedlayer_wall))
          (setq temp_wall_layer  (nth added_index wall_layer))
          (mapcar 'dclist '("all_wall" "selected_wall")
              (mapcar 'set '(temp_collectedlayer_wall temp_wall_layer)
                  (shiftitems (read (strcat "(" (get_tile "all_wall") ")")) temp_collectedlayer_wall temp_wall_layer)
              ))
          (set_tile "all_wall_slider" "0")
          (set_tile "selected_wall_file_slider" "0")
          (set_tile "selected_wall_slider" "0")
          (setq collectedlayer_wall (SubstNth temp_collectedlayer_wall selected_index collectedlayer_wall))
          (setq wall_layer (SubstNth temp_wall_layer added_index wall_layer))
          )))
  (action_tile "remove_wall"
      (vl-prin1-to-string
          '(progn
            (setq added_index (atoi (get_tile "selected_wall_file")))
            (setq sel_filename (nth added_index wall_file))
            (setq selected_index (vl-position sel_filename dwgname_list_shown))
            (setq temp_collectedlayer_wall  (nth selected_index collectedlayer_wall))
            (setq temp_wall_layer  (nth added_index wall_layer))
            (mapcar 'dclist '("selected_wall" "all_wall")
              (mapcar 'set '(temp_wall_layer temp_collectedlayer_wall)
                  (shiftitems  (read (strcat "(" (get_tile "selected_wall") ")")) temp_wall_layer temp_collectedlayer_wall)
              ))
            (setq collectedlayer_wall (SubstNth temp_collectedlayer_wall selected_index collectedlayer_wall))
            (setq wall_layer (SubstNth temp_wall_layer added_index wall_layer))
            
            (set_tile "source_wall" (itoa (vl-position sel_filename dwgname_list_shown)))
            (set_tile "all_wall_slider" "0")
            (set_tile "selected_wall_slider" "0")
            
            (if (null temp_wall_layer)
              (progn
                (setq wall_file (RemoveNth added_index wall_file))
                (setq wall_layer (RemoveNth added_index wall_layer))
                (start_list "selected_wall_file")
                (foreach itm wall_file (add_list itm))
                (end_list)
                (set_tile "selected_wall_file_slider" "0")
              )) 
            )))

  (action_tile "add_text"
      (vl-prin1-to-string
        '(progn
          (setq selected_index (atoi (get_tile "source_text")))
          (setq sel_filename (nth selected_index dwgname_list_shown))
          (if (boundp 'text_file)
            (progn
               (if (not (member sel_filename text_file))
                (progn
                 (setq text_file (append text_file (list sel_filename)))
                 (setq text_layer (append text_layer (list'())))
                )
               )
            )
            (progn
               (setq text_file (list sel_filename))
               (setq text_layer (list'()))
            ))
          (start_list "selected_text_file")
            (foreach itm text_file (add_list itm))
          (end_list)
          (setq added_index (vl-position sel_filename text_file))
          (set_tile "selected_text_file" (vl-princ-to-string added_index))
          
          (setq temp_collectedlayer_text  (nth selected_index collectedlayer_text))
          (setq temp_text_layer  (nth added_index text_layer))
          (mapcar 'dclist '("all_text" "selected_text")
              (mapcar 'set '(temp_collectedlayer_text temp_text_layer)
                  (shiftitems (read (strcat "(" (get_tile "all_text") ")")) temp_collectedlayer_text temp_text_layer)
              ))
          (set_tile "all_text_slider" "0")
          (set_tile "selected_text_file_slider" "0")
          (set_tile "selected_text_slider" "0")
          (setq collectedlayer_text (SubstNth temp_collectedlayer_text selected_index collectedlayer_text))
          (setq text_layer (SubstNth temp_text_layer added_index text_layer))
          )))
  (action_tile "remove_text"
      (vl-prin1-to-string
          '(progn
            (setq added_index (atoi (get_tile "selected_text_file")))
            (setq sel_filename (nth added_index text_file))
            (setq selected_index (vl-position sel_filename dwgname_list_shown))
            (setq temp_collectedlayer_text  (nth selected_index collectedlayer_text))
            (setq temp_text_layer  (nth added_index text_layer))
            (mapcar 'dclist '("selected_text" "all_text")
              (mapcar 'set '(temp_text_layer temp_collectedlayer_text)
                  (shiftitems  (read (strcat "(" (get_tile "selected_text") ")")) temp_text_layer temp_collectedlayer_text)
              ))
            (setq collectedlayer_text (SubstNth temp_collectedlayer_text selected_index collectedlayer_text))
            (setq text_layer (SubstNth temp_text_layer added_index text_layer))
            
            (set_tile "source_text" (itoa (vl-position sel_filename dwgname_list_shown)))
            (set_tile "all_text_slider" "0")
            (set_tile "selected_text_slider" "0")
            
            (if (null temp_text_layer)
              (progn
                (setq text_file (RemoveNth added_index text_file))
                (setq text_layer (RemoveNth added_index text_layer))
                (start_list "selected_text_file")
                (foreach itm text_file (add_list itm))
                (end_list)
                (set_tile "selected_text_file_slider" "0")
              ))
            )))
  
  (action_tile "add_pointer"
      (vl-prin1-to-string
        '(progn
          (setq selected_index (atoi (get_tile "source_pointer")))
          (setq sel_filename (nth selected_index dwgname_list_shown))
          (if (boundp 'pointer_file)
            (progn
               (if (not (member sel_filename pointer_file))
                (progn
                 (setq pointer_file (append pointer_file (list sel_filename)))
                 (setq pointer_layer (append pointer_layer (list'())))
                )
               )
            )
            (progn
               (setq pointer_file (list sel_filename))
               (setq pointer_layer (list'()))
            ))
          (start_list "selected_pointer_file")
            (foreach itm pointer_file (add_list itm))
          (end_list)
          (setq added_index (vl-position sel_filename pointer_file))
          (set_tile "selected_pointer_file" (vl-princ-to-string added_index))
          
          (setq temp_collectedlayer_pointer  (nth selected_index collectedlayer_pointer))
          (setq temp_pointer_layer  (nth added_index pointer_layer))
          (mapcar 'dclist '("all_pointer" "selected_pointer")
              (mapcar 'set '(temp_collectedlayer_pointer temp_pointer_layer)
                  (shiftitems (read (strcat "(" (get_tile "all_pointer") ")")) temp_collectedlayer_pointer temp_pointer_layer)
              ))
          (set_tile "all_pointer_slider" "0")
          (set_tile "selected_pointer_file_slider" "0")
          (set_tile "selected_pointer_slider" "0")
          (setq collectedlayer_pointer (SubstNth temp_collectedlayer_pointer selected_index collectedlayer_pointer))
          (setq pointer_layer (SubstNth temp_pointer_layer added_index pointer_layer))
          )))
  (action_tile "remove_pointer"
      (vl-prin1-to-string
          '(progn
            (setq added_index (atoi (get_tile "selected_pointer_file")))
            (setq sel_filename (nth added_index pointer_file))
            (setq selected_index (vl-position sel_filename dwgname_list_shown))
            (setq temp_collectedlayer_pointer  (nth selected_index collectedlayer_pointer))
            (setq temp_pointer_layer  (nth added_index pointer_layer))
            (mapcar 'dclist '("selected_pointer" "all_pointer")
              (mapcar 'set '(temp_pointer_layer temp_collectedlayer_pointer)
                  (shiftitems  (read (strcat "(" (get_tile "selected_pointer") ")")) temp_pointer_layer temp_collectedlayer_pointer)
              ))
            (setq collectedlayer_pointer (SubstNth temp_collectedlayer_pointer selected_index collectedlayer_pointer))
            (setq pointer_layer (SubstNth temp_pointer_layer added_index pointer_layer))
            
            (set_tile "source_pointer" (itoa (vl-position sel_filename dwgname_list_shown)))
            (set_tile "all_pointer_slider" "0")
            (set_tile "selected_pointer_slider" "0")
            
            (if (null temp_pointer_layer)
              (progn
                (setq pointer_file (RemoveNth added_index pointer_file))
                (setq pointer_layer (RemoveNth added_index pointer_layer))
                (start_list "selected_pointer_file")
                (foreach itm pointer_file (add_list itm))
                (end_list)
                (set_tile "selected_pointer_file_slider" "0")
              ))
            )))
  
  (action_tile "source_wall_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_wall_slider" "source_wall" dwgname_list_shown 3 "   ")))
  (action_tile "all_wall_slider" (vl-prin1-to-string '(slider_cut_restore_string "all_wall_slider" "all_wall" (nth (atoi (get_tile "source_wall")) collectedlayer_wall) 3 "   ")))
  (action_tile "selected_wall_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_wall_file_slider" "selected_wall_file" wall_file 3 "   ")))
  (action_tile "selected_wall_slider" (vl-prin1-to-string '(if (not (equal wall_file nil))
      (slider_cut_restore_string "selected_wall_slider" "selected_wall" (nth (atoi (get_tile "selected_wall_file")) wall_layer) 3 "   "))
      ))
  
  (action_tile "source_text_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_text_slider" "source_text" dwgname_list_shown 3 "   ")))
  (action_tile "all_text_slider" (vl-prin1-to-string '(slider_cut_restore_string "all_text_slider" "all_text" (nth (atoi (get_tile "source_text")) collectedlayer_text) 3 "   ")))
  (action_tile "selected_text_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_text_file_slider" "selected_text_file" text_file 3 "   ")))
  (action_tile "selected_text_slider" (vl-prin1-to-string '(if (not (equal text_file nil))
      (slider_cut_restore_string "selected_text_slider" "selected_text" (nth (atoi (get_tile "selected_text_file")) text_layer) 3 "   "))
      ))
  
  (action_tile "source_pointer_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_pointer_slider" "source_pointer" dwgname_list_shown 3 "   ")))
  (action_tile "all_pointer_slider" (vl-prin1-to-string '(slider_cut_restore_string "all_pointer_slider" "all_pointer" (nth (atoi (get_tile "source_pointer")) collectedlayer_pointer) 3 "   ")))
  (action_tile "selected_pointer_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_pointer_file_slider" "selected_pointer_file" pointer_file 3 "   ")))
  (action_tile "selected_pointer_slider" (vl-prin1-to-string '(if (not (equal pointer_file nil))
      (slider_cut_restore_string "selected_pointer_slider" "selected_pointer" (nth (atoi (get_tile "selected_pointer_file")) pointer_layer) 3 "   "))
      ))
  
  (action_tile "accept"
  (vl-prin1-to-string
          '(progn
            (if (and
              (equal (vl-sort wall_file '<) (vl-sort text_file '<))
              (equal (vl-sort text_file '<) (vl-sort pointer_file '<))
            )
          (done_dialog)
          (alert "Please make sure the Selected File(s) are all the same ! (Including between Vertical Rebar and Horizontal Shear Rebar)"))
  )))
  
  (action_tile "cancel"
  (strcat
  "(quit)"
  ))
  (start_dialog)
  (unload_dialog dcl_id)

  (setq dcl_id_2 (load_dialog "dcl\\sh_rebar_layer_selection.dcl")) ; change directory path to known location
  (if (not (new_dialog "layer_selection" dcl_id_2))
  (exit)
  )

  (start_list "source_text")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list) 
  (action_tile "source_text" 
    (vl-prin1-to-string
      '(progn
        (setq selected_index (atoi (get_tile "source_text")))
        (start_list "all_text")
        (foreach itm (nth selected_index collectedlayer_text_2) (add_list itm))
        (end_list)
        (set_tile "all_text" "0")
        (set_tile "all_text_slider" "0")
      )
    )
  )
  
  (start_list "source_wall")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list)
  (action_tile "source_wall" 
    (vl-prin1-to-string
      '(progn
        (setq selected_index (atoi (get_tile "source_wall")))
        (start_list "all_wall")
        (foreach itm (nth selected_index collectedlayer_wall_2) (add_list itm))
        (end_list)
        (set_tile "all_wall" "0")
        (set_tile "all_wall_slider" "0")
      )
    )
  )
  
  (start_list "source_pointer")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list) 
  (action_tile "source_pointer" 
    (vl-prin1-to-string
      '(progn
        (setq selected_index (atoi (get_tile "source_pointer")))
        (start_list "all_pointer")
        (foreach itm (nth selected_index collectedlayer_pointer_2) (add_list itm))
        (end_list)
        (set_tile "all_pointer" "0")
        (set_tile "all_pointer_slider" "0")
      )
    )
  )
  
  (start_list "all_text")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "all_text" "")
  
  (start_list "all_wall")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "all_wall" "")
  
  (start_list "all_pointer")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "all_pointer" "")
  
  (action_tile "selected_text_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_text_file")))
        (start_list "selected_text")
        (foreach itm (nth added_index text_layer_2) (add_list itm))
        (end_list)
        (set_tile "selected_text_slider" "0")
        )
    )
  )
  
  (action_tile "selected_wall_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_wall_file")))
        (start_list "selected_wall")
        (foreach itm (nth added_index wall_layer_2) (add_list itm))
        (end_list)
        (set_tile "selected_wall_slider" "0")
      )
    )
  )
  
  (action_tile "selected_pointer_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_pointer_file")))
        (start_list "selected_pointer")
        (foreach itm (nth added_index pointer_layer_2) (add_list itm))
        (end_list)
        (set_tile "selected_pointer_slider" "0")
      )
    )
  )

  (action_tile "add_text"
      (vl-prin1-to-string
        '(progn
          (setq selected_index (atoi (get_tile "source_text")))
          (setq sel_filename (nth selected_index dwgname_list_shown))
          (if (boundp 'text_file_2)
            (progn
               (if (not (member sel_filename text_file_2))
                (progn
                 (setq text_file_2 (append text_file_2 (list sel_filename)))
                 (setq text_layer_2 (append text_layer_2 (list'())))
                )
               )
            )
            (progn
               (setq text_file_2 (list sel_filename))
               (setq text_layer_2 (list'()))
            ))
          (start_list "selected_text_file")
            (foreach itm text_file_2 (add_list itm))
          (end_list)
          (setq added_index (vl-position sel_filename text_file_2))
          (set_tile "selected_text_file" (vl-princ-to-string added_index))
          
          (setq temp_collectedlayer_text_2  (nth selected_index collectedlayer_text_2))
          (setq temp_text_layer_2  (nth added_index text_layer_2))
          (mapcar 'dclist '("all_text" "selected_text")
              (mapcar 'set '(temp_collectedlayer_text_2 temp_text_layer_2)
                  (shiftitems (read (strcat "(" (get_tile "all_text") ")")) temp_collectedlayer_text_2 temp_text_layer_2)
              ))
          (set_tile "all_text_slider" "0")
          (set_tile "selected_text_file_slider" "0")
          (set_tile "selected_text_slider" "0")
          (setq collectedlayer_text_2 (SubstNth temp_collectedlayer_text_2 selected_index collectedlayer_text_2))
          (setq text_layer_2 (SubstNth temp_text_layer_2 added_index text_layer_2))
          )))
  (action_tile "remove_text"
      (vl-prin1-to-string
          '(progn
            (setq added_index (atoi (get_tile "selected_text_file")))
            (setq sel_filename (nth added_index text_file_2))
            (setq selected_index (vl-position sel_filename dwgname_list_shown))
            (setq temp_collectedlayer_text_2  (nth selected_index collectedlayer_text_2))
            (setq temp_text_layer_2  (nth added_index text_layer_2))
            (mapcar 'dclist '("selected_text" "all_text")
              (mapcar 'set '(temp_text_layer_2 temp_collectedlayer_text_2)
                  (shiftitems  (read (strcat "(" (get_tile "selected_text") ")")) temp_text_layer_2 temp_collectedlayer_text_2)
              ))
            (setq collectedlayer_text_2 (SubstNth temp_collectedlayer_text_2 selected_index collectedlayer_text_2))
            (setq text_layer_2 (SubstNth temp_text_layer_2 added_index text_layer_2))
            
            (set_tile "source_text" (itoa (vl-position sel_filename dwgname_list_shown)))
            (set_tile "all_text_slider" "0")
            (set_tile "selected_text_slider" "0")
            
            (if (null temp_text_layer_2)
              (progn
                (setq text_file_2 (RemoveNth added_index text_file_2))
                (setq text_layer_2 (RemoveNth added_index text_layer_2))
                (start_list "selected_text_file")
                (foreach itm text_file_2 (add_list itm))
                (end_list)
                (set_tile "selected_text_file_slider" "0")
              ))
            )))
  
  (action_tile "add_wall"
      (vl-prin1-to-string
        '(progn
          (setq selected_index (atoi (get_tile "source_wall")))
          (setq sel_filename (nth selected_index dwgname_list_shown))
          (if (boundp 'wall_file_2)
            (progn
               (if (not (member sel_filename wall_file_2))
                (progn
                 (setq wall_file_2 (append wall_file_2 (list sel_filename)))
                 (setq wall_layer_2 (append wall_layer_2 (list'())))
                )
               )
            )
            (progn
               (setq wall_file_2 (list sel_filename))
               (setq wall_layer_2 (list'()))
            ))
          (start_list "selected_wall_file")
            (foreach itm wall_file_2 (add_list itm))
          (end_list)
          (setq added_index (vl-position sel_filename wall_file_2))
          (set_tile "selected_wall_file" (vl-princ-to-string added_index))
          
          (setq temp_collectedlayer_wall_2  (nth selected_index collectedlayer_wall_2))
          (setq temp_wall_layer_2  (nth added_index wall_layer_2))
          (mapcar 'dclist '("all_wall" "selected_wall")
              (mapcar 'set '(temp_collectedlayer_wall_2 temp_wall_layer_2)
                  (shiftitems (read (strcat "(" (get_tile "all_wall") ")")) temp_collectedlayer_wall_2 temp_wall_layer_2)
              ))
          (set_tile "all_wall_slider" "0")
          (set_tile "selected_wall_file_slider" "0")
          (set_tile "selected_wall_slider" "0")
          (setq collectedlayer_wall_2 (SubstNth temp_collectedlayer_wall_2 selected_index collectedlayer_wall_2))
          (setq wall_layer_2 (SubstNth temp_wall_layer_2 added_index wall_layer_2))
          )))
  (action_tile "remove_wall"
      (vl-prin1-to-string
          '(progn
            (setq added_index (atoi (get_tile "selected_wall_file")))
            (setq sel_filename (nth added_index wall_file_2))
            (setq selected_index (vl-position sel_filename dwgname_list_shown))
            (setq temp_collectedlayer_wall_2  (nth selected_index collectedlayer_wall_2))
            (setq temp_wall_layer_2  (nth added_index wall_layer_2))
            (mapcar 'dclist '("selected_wall" "all_wall")
              (mapcar 'set '(temp_wall_layer_2 temp_collectedlayer_wall_2)
                  (shiftitems  (read (strcat "(" (get_tile "selected_wall") ")")) temp_wall_layer_2 temp_collectedlayer_wall_2)
              ))
            (setq collectedlayer_wall_2 (SubstNth temp_collectedlayer_wall_2 selected_index collectedlayer_wall_2))
            (setq wall_layer_2 (SubstNth temp_wall_layer_2 added_index wall_layer_2))
            
            (set_tile "source_wall" (itoa (vl-position sel_filename dwgname_list_shown)))
            (set_tile "all_wall_slider" "0")
            (set_tile "selected_wall_slider" "0")
            
            (if (null temp_wall_layer_2)
              (progn
                (setq wall_file_2 (RemoveNth added_index wall_file_2))
                (setq wall_layer_2 (RemoveNth added_index wall_layer_2))
                (start_list "selected_wall_file")
                (foreach itm wall_file_2 (add_list itm))
                (end_list)
                (set_tile "selected_wall_file_slider" "0")
              ))
            )))
  
  (action_tile "add_pointer"
      (vl-prin1-to-string
        '(progn
          (setq selected_index (atoi (get_tile "source_pointer")))
          (setq sel_filename (nth selected_index dwgname_list_shown))
          (if (boundp 'pointer_file_2)
            (progn
               (if (not (member sel_filename pointer_file_2))
                (progn
                 (setq pointer_file_2 (append pointer_file_2 (list sel_filename)))
                 (setq pointer_layer_2 (append pointer_layer_2 (list'())))
                )
               )
            )
            (progn
               (setq pointer_file_2 (list sel_filename))
               (setq pointer_layer_2 (list'()))
            ))
          (start_list "selected_pointer_file")
            (foreach itm pointer_file_2 (add_list itm))
          (end_list)
          (setq added_index (vl-position sel_filename pointer_file_2))
          (set_tile "selected_pointer_file" (vl-princ-to-string added_index))
          
          (setq temp_collectedlayer_pointer_2  (nth selected_index collectedlayer_pointer_2))
          (setq temp_pointer_layer_2  (nth added_index pointer_layer_2))
          (mapcar 'dclist '("all_pointer" "selected_pointer")
              (mapcar 'set '(temp_collectedlayer_pointer_2 temp_pointer_layer_2)
                  (shiftitems (read (strcat "(" (get_tile "all_pointer") ")")) temp_collectedlayer_pointer_2 temp_pointer_layer_2)
              ))
          (set_tile "all_pointer_slider" "0")
          (set_tile "selected_pointer_file_slider" "0")
          (set_tile "selected_pointer_slider" "0")
          (setq collectedlayer_pointer_2 (SubstNth temp_collectedlayer_pointer_2 selected_index collectedlayer_pointer_2))
          (setq pointer_layer_2 (SubstNth temp_pointer_layer_2 added_index pointer_layer_2))
          )))
  (action_tile "remove_pointer"
      (vl-prin1-to-string
          '(progn
            (setq added_index (atoi (get_tile "selected_pointer_file")))
            (setq sel_filename (nth added_index pointer_file_2))
            (setq selected_index (vl-position sel_filename dwgname_list_shown))
            (setq temp_collectedlayer_pointer_2  (nth selected_index collectedlayer_pointer_2))
            (setq temp_pointer_layer_2  (nth added_index pointer_layer_2))
            (mapcar 'dclist '("selected_pointer" "all_pointer")
              (mapcar 'set '(temp_pointer_layer_2 temp_collectedlayer_pointer_2)
                  (shiftitems  (read (strcat "(" (get_tile "selected_pointer") ")")) temp_pointer_layer_2 temp_collectedlayer_pointer_2)
              ))
            (setq collectedlayer_pointer_2 (SubstNth temp_collectedlayer_pointer_2 selected_index collectedlayer_pointer_2))
            (setq pointer_layer_2 (SubstNth temp_pointer_layer_2 added_index pointer_layer_2))
            
            (set_tile "source_pointer" (itoa (vl-position sel_filename dwgname_list_shown)))
            (set_tile "all_pointer_slider" "0")
            (set_tile "selected_pointer_slider" "0")
            
            (if (null temp_pointer_layer_2)
              (progn
                (setq pointer_file_2 (RemoveNth added_index pointer_file_2))
                (setq pointer_layer_2 (RemoveNth added_index pointer_layer_2))
                (start_list "selected_pointer_file")
                (foreach itm pointer_file_2 (add_list itm))
                (end_list)
                (set_tile "selected_pointer_file_slider" "0")
              ))
            )))
  
  (action_tile "source_text_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_text_slider" "source_text" dwgname_list_shown 3 "   ")))
  (action_tile "all_text_slider" (vl-prin1-to-string '(slider_cut_restore_string "all_text_slider" "all_text" (nth (atoi (get_tile "source_text")) collectedlayer_text_2) 3 "   ")))
  (action_tile "selected_text_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_text_file_slider" "selected_text_file" text_file_2 3 "   ")))
  (action_tile "selected_text_slider" (vl-prin1-to-string '(if (not (equal text_file_2 nil))
      (slider_cut_restore_string "selected_text_slider" "selected_text" (nth (atoi (get_tile "selected_text_file")) text_layer_2) 3 "   "))
      ))
  
  (action_tile "source_wall_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_wall_slider" "source_wall" dwgname_list_shown 3 "   ")))
  (action_tile "all_wall_slider" (vl-prin1-to-string '(slider_cut_restore_string "all_wall_slider" "all_wall" (nth (atoi (get_tile "source_wall")) collectedlayer_wall_2) 3 "   ")))
  (action_tile "selected_wall_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_wall_file_slider" "selected_wall_file" wall_file_2 3 "   ")))
  (action_tile "selected_wall_slider" (vl-prin1-to-string '(if (not (equal wall_file_2 nil))
      (slider_cut_restore_string "selected_wall_slider" "selected_wall" (nth (atoi (get_tile "selected_wall_file")) wall_layer_2) 3 "   "))
      ))
  
  (action_tile "source_pointer_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_pointer_slider" "source_pointer" dwgname_list_shown 3 "   ")))
  (action_tile "all_pointer_slider" (vl-prin1-to-string '(slider_cut_restore_string "all_pointer_slider" "all_pointer" (nth (atoi (get_tile "source_pointer")) collectedlayer_pointer_2) 3 "   ")))
  (action_tile "selected_pointer_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_pointer_file_slider" "selected_pointer_file" pointer_file_2 3 "   ")))
  (action_tile "selected_pointer_slider" (vl-prin1-to-string '(if (not (equal pointer_file_2 nil))
      (slider_cut_restore_string "selected_pointer_slider" "selected_pointer" (nth (atoi (get_tile "selected_pointer_file")) pointer_layer_2) 3 "   "))
      ))
  
  (action_tile "accept"
  (vl-prin1-to-string
          '(progn
            (if (and
              (equal (vl-sort wall_file_2 '<) (vl-sort text_file_2 '<))
              (equal (vl-sort text_file_2 '<) (vl-sort pointer_file_2 '<))
              (equal (vl-sort wall_file_2 '<) (vl-sort wall_file '<))
              (equal (vl-sort text_file_2 '<) (vl-sort text_file '<))
              (equal (vl-sort pointer_file_2 '<) (vl-sort pointer_file '<))
            )
          (done_dialog)
          (alert "Please make sure the Selected File(s) are all the same ! (Including between Vertical Rebar and Horizontal Shear Rebar)"))
  )))
  
  (action_tile "cancel"
  (strcat
  "(quit)"
  ))
  (start_dialog)
  (unload_dialog dcl_id_2)
  (setq target_layer_big (list (list wall_file text_file pointer_file wall_layer text_layer pointer_layer) (list text_file_2 wall_file_2 pointer_file_2 text_layer_2 wall_layer_2 pointer_layer_2)))
)
(defun slider_cut_restore_string (scrollbar_name listbox_name list_shown remove_n_string space_added)
  (setq selected_index (atoi (get_tile listbox_name)))
  (setq scrollbar_value (atoi (get_tile scrollbar_name)))
  (setq temp_list list_shown)
  (setq processed_temp_list '()) ; Initialize an empty list to store processed strings

  (foreach str temp_list
    (setq processed_str str)
    (repeat scrollbar_value
      (setq processed_str (substr processed_str remove_n_string)) ; Remove first 2 characters
      (setq processed_str (strcat processed_str space_added)) ; Add 2 spaces
    )
    (setq processed_temp_list (cons processed_str processed_temp_list))
  )

  (setq processed_temp_list (reverse processed_temp_list))
  (start_list listbox_name)
  (foreach itm processed_temp_list (add_list itm))
  (end_list)
  (set_tile listbox_name (itoa selected_index))
)
(defun RemoveNth ( n l )
    (if (and l (< 0 n))
        (cons (car l) (RemoveNth (1- n) (cdr l)))
        (cdr l)
    )
)
(defun SubstNth ( a n l / i )
    (setq i -1)
    (mapcar '(lambda ( x ) (if (= (setq i (1+ i)) n) a x)) l)
)
(defun dclist ( key lst )
    (start_list key)
    (foreach itm lst (add_list itm))
    (end_list)
)

(defun shiftitems ( idx lb1 lb2 / int )
    (setq int -1
          lb2 (reverse lb2)
          lb1 (vl-remove-if '(lambda ( x ) (if (member (setq int (1+ int)) idx) (setq lb2 (cons x lb2)))) lb1)
    )
    (list lb1 (reverse lb2))
)
(defun mainloop1 (dirpath dwgname_list target_layer)
  (setq wall_file (nth 0 target_layer))
  (setq text_file (nth 1 target_layer))
  (setq wall_layer (nth 2 target_layer))
  (setq text_layer (nth 3 target_layer))

  (setq line_lst '(("FileName" "EntityName" "Layer" "Length" "StartCoor" "EndCoor")))
  (setq text_lst '(("FileName" "EntityName" "ObjectType" "RotationAngle" "CentreCoor" "StartCoor" "EndCoor" "Text")))
  (makedsd dirpath dwgname_list "-Layout1.pdf" "PUBLIST.dsd")
  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (vla-StartUndoMark doc)
    
    (if (and (member dwgname wall_file) (member dwgname text_file))
      (progn
        (setq wall_file_index (vl-position dwgname wall_file))
        (setq line_lst (append line_lst (extractlineinfo doc dwgname (nth wall_file_index wall_layer))))
        
        (setq text_file_index (vl-position dwgname text_file))
        (setq combi_layer (append (nth wall_file_index wall_layer) (nth text_file_index text_layer)))
        (setq text_lst (append text_lst (extracttextinfo doc dwgname combi_layer)))
        
        (filterlayer doc combi_layer)

      )
    )
    
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq dwgname_list (cdr dwgname_list))
  )
  (command "-Publish" (strcat dirpath "\\" "PUBLIST.dsd") )
  (_writecsv "W" (strcat dirpath "\\Line Info.csv") line_lst)
  (_writecsv "w" (strcat dirpath "\\Text Info.csv") text_lst)
)

(defun publish_all_folder(dirpath dwgname_list)
  (makedsd dirpath dwgname_list "-Layout1.pdf" "PUBLIST.dsd")
  (command "-Publish" (strcat dirpath "\\" "PUBLIST.dsd") )
)

(defun publish_bylayer_folder (dirpath dwgname_list target_layer outputpath dsd_path)
  (makedsd dirpath dwgname_list outputpath dsd_path)

  (setq target_layer (car target_layer))
  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (vla-StartUndoMark doc)
    
    
    (filterlayer doc target_layer)
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq dwgname_list (cdr dwgname_list))
  )
  (command "-Publish" (strcat dirpath "\\" dsd_path) )

)

(defun mainloop2 (dirpath dwgname_list target_layer)
  (setq wall_file (nth 0 target_layer))
  (setq text_file (nth 1 target_layer))
  (setq wall_layer (nth 2 target_layer))
  (setq text_layer (nth 3 target_layer))
  (setq line_lst '(("FileName" "EntityName" "Layer" "Length" "StartCoor" "EndCoor")))
  (makedsd dirpath dwgname_list "-Layout1.pdf" "PUBLIST.dsd")
  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (vla-StartUndoMark doc)
    
    (if (and (member dwgname wall_file) (member dwgname text_file))
      (progn
        (setq wall_file_index (vl-position dwgname wall_file))
        (setq line_lst (append line_lst (extractlineinfo doc dwgname (nth wall_file_index wall_layer))))
        
        (setq text_file_index (vl-position dwgname text_file))
        (setq combi_layer (append (nth wall_file_index wall_layer) (nth text_file_index text_layer)))
        (setq text_lst (append text_lst (extracttextinfo doc dwgname combi_layer)))
        
        (filterlayer doc combi_layer)

      )
    )
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq dwgname_list (cdr dwgname_list))
  )
  (command "-Publish" (strcat dirpath "\\" "PUBLIST.dsd") )
  (_writecsv "W" (strcat dirpath "\\Line Info.csv") line_lst)
  (_writecsv "w" (strcat dirpath "\\Text info.csv") text_lst)
)

(defun mainloop3 (filepath dirpath filename)
  (vl-load-com)
  (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) *temp*))
  (vla-StartUndoMark doc)
  (setq layouts (vla-get-Layouts doc))
  (setq exportable "False")
  (vlax-for layout layouts
    (if (vl-string-search "1" (vla-get-Name layout))
      (progn
      (setq *layoutname_list* (append *layoutname_list* (list (vla-get-Name layout))))
      (set-layout-plotter-config doc (vla-get-Name layout) "AutoCAD PDF (General Documentation).pc3")
      (setq exportable  "True")
      )
    )
  )
  (if (equal exportable "False")
    (progn
      (princ (strcat "Layout1 / 配置1 is not found in " filename ", there will be problem exporting the pdf"))
      (setq *layoutname_list* (/ 1 0))
    )
  )
  (makedsd dirpath filename "-Layout1.pdf" "PUBLIST.dsd")
  (command "-Publish" (strcat dirpath "\\" "PUBLIST.dsd") )
  
  (vla-purgeall doc)
  (vla-EndUndoMark doc)
  (vla-save doc)
  (vla-close doc)
)

(defun mainloop4 (dirpath dwgname_list dwgname_list_2 target_layer1 target_layer2 )
  (setq dwgname_list_3 dwgname_list_2)
  (setq rebar_file (nth 0 target_layer1))
  (setq text_file (nth 1 target_layer1))
  (setq pointer_file (nth 2 target_layer1))
  (setq rebar_layer (nth 3 target_layer1))
  (setq text_layer (nth 4 target_layer1))
  (setq pointer_layer (nth 5 target_layer1))
  
  (setq text_file2 (nth 0 target_layer2))
  (setq rebar_file2 (nth 1 target_layer2))
  (setq pointer_file2 (nth 2 target_layer2))
  (setq text_layer2 (nth 3 target_layer2))
  (setq rebar_layer2 (nth 4 target_layer2))
  (setq pointer_layer2 (nth 5 target_layer2))
  
  (setq line_lst '(("FileName" "EntityName" "Layer" "Length" "StartCoor" "EndCoor")))
  (setq helper_lst '(("FileName" "EntityName" "ObjectType" "BasePoint" "UpLeftPoint" "DownRightPoint")))
  (setq text_lst '(("FileName" "EntityName" "ObjectType" "RotationAngle" "CentreCoor" "Height" "Width" "Text")))
  (setq text_lst2 '(("FileName" "EntityName" "ObjectType" "RotationAngle" "CentreCoor" "Height" "Width" "Text")))
  (setq line_lst2 '(("FileName" "EntityName" "Layer" "Length" "StartCoor" "EndCoor")))
  (setq helper_lst2 '(("FileName" "EntityName" "ObjectType" "BasePoint" "UpLeftPoint" "DownRightPoint")))
  
  (setq layoutname_list_backup *layoutname_list*)
  (makedsd dirpath dwgname_list "-Layout1.pdf" "PUBLIST.dsd")
  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (vla-StartUndoMark doc)
    
    (if (and (member dwgname rebar_file) (member dwgname text_file) (member dwgname pointer_file))
      (progn
        (setq rebar_file_index (vl-position dwgname rebar_file))
        (setq text_file_index (vl-position dwgname text_file))
        (setq pointer_file_index (vl-position dwgname pointer_file))
        (setq combi_layer (append (nth rebar_file_index rebar_layer) (nth text_file_index text_layer)))

        (filterlayer doc (nth text_file_index text_layer))
        (setq target_layer_name (append (nth rebar_file_index rebar_layer) '()))
        (setq helper_layer_name (append  (nth pointer_file_index pointer_layer) '()))
        
        ;Extract the line2
        (setq lst1 '())
        (setq lst2 '())
        (setq ss (vla-get-modelspace doc ))
        (while target_layer_name
          (vlax-for obj ss
            (setq x (vlax-vla-object->ename obj))
            (if 
              (and
              (eq (vla-get-objectname obj) "AcDbLine")
              (= (vla-get-layer obj) (car target_layer_name))
              )
              (progn
              (setq ep (cdr (assoc 11 (entget x))))
              (setq sp (cdr (assoc 10 (entget x))))
              (foreach num ep
                  (setq num_str (rtos num 2 2))
                  (setq ep (subst num_str num ep))
              )
              (foreach num sp
                  (setq num_str (rtos num 2 2))
                  (setq sp (subst num_str num sp))
              )
              (setq len (vla-get-length obj))
              (setq lay (vla-get-layer obj))
              (setq lst2 (cons ep lst2))
              (setq lst2 (cons sp lst2))
              (setq lst2 (cons len lst2))
              (setq lst2 (cons lay lst2))
              (setq lst2 (cons x lst2))
              (setq lst2 (cons dwgname lst2))
              (setq lst1 (cons lst2 lst1))
              (setq lst2 '())
              )
            )
          )
          (setq target_layer_name (cdr target_layer_name))
        )

        (setq lst1 lst1)
        (setq line_lst (append line_lst lst1))
        ;end

        ;Extract the helper line
        (setq lst1 '())
        (setq lst2 '())
        (setq ss (vla-get-modelspace doc ))
        (while helper_layer_name
          (vlax-for obj ss
            (setq x (vlax-vla-object->ename obj))
            (if 
              (and
                (eq (vla-get-objectname obj) "AcDbBlockReference")
                (= (vla-get-layer obj) (car helper_layer_name))
              )
              (progn
                ;(setq lst2 (cons (vla-getboundingbox obj)) lst2)
                (if (vlax-method-applicable-p obj 'GETBOUNDINGBOX)
                  (progn (vla-getboundingbox obj 'min 'max)
                  (setq DownLeftPoint (vlax-safearray->list min));_ the down left point
                  (setq UpRightPoint (vlax-safearray->list max));_ the Up Right point
                  (setq UpLeftPoint (list (rtos (car DownLeftPoint) 2 2) (rtos (cadr UpRightPoint) 2 2)))
                  (setq DownRightPoint (list (rtos (car UpRightPoint) 2 2) (rtos (cadr DownLeftPoint) 2 2)))
                  )
                )
                (setq BasePoint (cdr (assoc 10 (entget x))))
                (foreach num BasePoint
                  (setq num_str (rtos num 2 2))
                  (setq BasePoint (subst num_str num BasePoint))
                )
                (setq lst2 (cons DownRightPoint lst2)) 
                (setq lst2 (cons UpLeftPoint lst2))
                (setq lst2 (cons BasePoint lst2))
                (setq lst2 (cons (vla-get-objectname obj) lst2))
                (setq lst2 (cons x lst2))
                (setq lst2 (cons dwgname lst2))
                (setq lst1 (cons lst2 lst1))
                (setq lst2 '())
              )
            )
          )
          (setq helper_layer_name (cdr helper_layer_name))
        )
        (setq lst1 lst1)
        (setq helper_lst (append helper_lst lst1))
        ;end

        ;Extract the text
        (setq lst1 '())
        (setq lst2 '())
        (setq ss (vla-get-modelspace doc ))
        (vlax-for obj ss
          (setq x (vlax-vla-object->ename obj))
          (if 
            (and
              (eq (vla-get-objectname obj) "AcDbText")
              (or
                (vl-string-search "GL" (vl-princ-to-string (assoc 1 (entget x))))
                (vl-string-search "EL" (vl-princ-to-string (assoc 1 (entget x))))
                (vl-string-search "@" (vl-princ-to-string (assoc 1 (entget x))))
                (vl-string-search "SIDE" (vl-princ-to-string (assoc 1 (entget x))))
              )
            )
            (progn
              (setq lst2 (cons (cdr (assoc 1 (entget x))) lst2))
              (setq lst2 (cons (cdr (assoc 41 (entget x))) lst2))
              (setq lst2 (cons (cdr (assoc 40 (entget x))) lst2))
              (setq CentreCoor (cdr (assoc 10 (entget x))))
                (foreach num CentreCoor
                  (setq num_str (rtos num 2 2))
                  (setq CentreCoor (subst num_str num CentreCoor))
              )
              (setq lst2 (cons CentreCoor lst2))
              (setq lst2 (cons (cdr (assoc 50 (entget x))) lst2))
              (setq lst2 (cons (vla-get-objectname obj) lst2))
              (setq lst2 (cons x lst2))
              (setq lst2 (cons dwgname lst2))
              (setq lst1 (cons lst2 lst1))
              (setq lst2 '())
            )
          )
        )
        (setq lst1 lst1)
        (setq text_lst (append text_lst lst1))
        ;end
        
      )
    )
    
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq dwgname_list (cdr dwgname_list))
  )
  (command "-Publish" (strcat dirpath "\\" "PUBLIST.dsd") )
  (_writecsv "W" (strcat dirpath "\\Helper Line Info.csv") helper_lst)
  (_writecsv "W" (strcat dirpath "\\Vertical Line Info.csv") line_lst)
  (_writecsv "W" (strcat dirpath "\\Text Info.csv") text_lst)
  
  (setq *layoutname_list* layoutname_list_backup)
  (makedsd dirpath dwgname_list_2 "-Layout1_2_ref.pdf" "PUBLIST_2.dsd")
  (while dwgname_list_2
    (setq dwgname (car dwgname_list_2))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (vla-StartUndoMark doc)
    
    (if (and (member dwgname rebar_file2) (member dwgname text_file2) (member dwgname pointer_file2))
      (progn
        (setq text_file_index2 (vl-position dwgname text_file2))
        (setq rebar_file_index2 (vl-position dwgname rebar_file2))
        (setq pointer_file_index2 (vl-position dwgname pointer_file2))
        
        (filterlayer doc (nth rebar_file_index2 rebar_layer2))
        (setq target_layer_name2 (append (nth rebar_file_index2 rebar_layer2) '()))
        (setq helper_layer_name2 (append  (nth pointer_file_index2 pointer_layer2) '()))
        
        ;Extract the text2
        (setq lst1 '())
        (setq lst2 '())
        (setq ss (vla-get-modelspace doc ))
        (vlax-for obj ss
          (setq x (vlax-vla-object->ename obj))
          (if 
            (and
              (eq (vla-get-objectname obj) "AcDbText")
              (or
                (vl-string-search "GL" (vl-princ-to-string (assoc 1 (entget x))))
                (vl-string-search "EL" (vl-princ-to-string (assoc 1 (entget x))))
                (vl-string-search "@" (vl-princ-to-string (assoc 1 (entget x))))
                (vl-string-search "SIDE" (vl-princ-to-string (assoc 1 (entget x))))
              )
            )
            (progn
              (setq lst2 (cons (cdr (assoc 1 (entget x))) lst2))
              (setq lst2 (cons (cdr (assoc 41 (entget x))) lst2))
              (setq lst2 (cons (cdr (assoc 40 (entget x))) lst2))
              (setq CentreCoor (cdr (assoc 10 (entget x))))
                (foreach num CentreCoor
                  (setq num_str (rtos num 2 2))
                  (setq CentreCoor (subst num_str num CentreCoor))
              )
              (setq lst2 (cons CentreCoor lst2))
              (setq lst2 (cons (cdr (assoc 50 (entget x))) lst2))
              (setq lst2 (cons (vla-get-objectname obj) lst2))
              (setq lst2 (cons x lst2))
              (setq lst2 (cons dwgname lst2))
              (setq lst1 (cons lst2 lst1))
              (setq lst2 '())
            )
          )
        )
        (setq lst1 lst1)
        (setq text_lst2 (append text_lst2 lst1))
        ;end
        
        ;Extract the line2
        (setq lst1 '())
        (setq lst2 '())
        (setq ss (vla-get-modelspace doc ))
        (while target_layer_name2
          (vlax-for obj ss
            (setq x (vlax-vla-object->ename obj))
            (if 
              (and
              (eq (vla-get-objectname obj) "AcDbLine")
              (= (vla-get-layer obj) (car target_layer_name2))
              )
              (progn
              (setq ep (cdr (assoc 11 (entget x))))
              (setq sp (cdr (assoc 10 (entget x))))
              (foreach num ep
                  (setq num_str (rtos num 2 2))
                  (setq ep (subst num_str num ep))
              )
              (foreach num sp
                  (setq num_str (rtos num 2 2))
                  (setq sp (subst num_str num sp))
              )
              (setq len (vla-get-length obj))
              (setq lay (vla-get-layer obj))
              (setq lst2 (cons ep lst2))
              (setq lst2 (cons sp lst2))
              (setq lst2 (cons len lst2))
              (setq lst2 (cons lay lst2))
              (setq lst2 (cons x lst2))
              (setq lst2 (cons dwgname lst2))
              (setq lst1 (cons lst2 lst1))
              (setq lst2 '())
              )
            )
          )
          (setq target_layer_name2 (cdr target_layer_name2))
        )

        (setq lst1 lst1)
        (setq line_lst2 (append line_lst2 lst1))
        ;end
        
        
        ;Extract the helper line2
        (setq lst1 '())
        (setq lst2 '())
        (setq ss (vla-get-modelspace doc ))
        (while helper_layer_name2
          (vlax-for obj ss
            (setq x (vlax-vla-object->ename obj))
            (if 
              (and
                (eq (vla-get-objectname obj) "AcDbBlockReference")
                (= (vla-get-name obj) (car helper_layer_name2))
              )
              (progn
                ;(setq lst2 (cons (vla-getboundingbox obj)) lst2)
                (if (vlax-method-applicable-p obj 'GETBOUNDINGBOX)
                  (progn (vla-getboundingbox obj 'min 'max)
                  (setq DownLeftPoint (vlax-safearray->list min));_ the down left point
                  (setq UpRightPoint (vlax-safearray->list max));_ the Up Right point
                  (setq UpLeftPoint (list (rtos (car DownLeftPoint) 2 2) (rtos (cadr UpRightPoint) 2 2)))
                  (setq DownRightPoint (list (rtos (car UpRightPoint) 2 2) (rtos (cadr DownLeftPoint) 2 2)))
                  )
                )
                (setq BasePoint (cdr (assoc 10 (entget x))))
                (foreach num BasePoint
                  (setq num_str (rtos num 2 2))
                  (setq BasePoint (subst num_str num BasePoint))
                )
                (setq lst2 (cons DownRightPoint lst2)) 
                (setq lst2 (cons UpLeftPoint lst2))
                (setq lst2 (cons BasePoint lst2))
                (setq lst2 (cons (vla-get-objectname obj) lst2))
                (setq lst2 (cons x lst2))
                (setq lst2 (cons dwgname lst2))
                (setq lst1 (cons lst2 lst1))
                (setq lst2 '())
              )
            )
          )
          (setq helper_layer_name2 (cdr helper_layer_name2))
        )
        (setq lst1 lst1)
        (setq helper_lst2 (append helper_lst2 lst1))
      )
    )
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq dwgname_list_2 (cdr dwgname_list_2))
  )
  
  (command "-Publish" (strcat dirpath "\\" "PUBLIST_2.dsd") )
  (_writecsv "W" (strcat dirpath "\\SH Text Info.csv") text_lst2)
  (_writecsv "W" (strcat dirpath "\\SH Line Info.csv") line_lst2)
  (_writecsv "W" (strcat dirpath "\\SH Helper Line Info.csv") helper_lst2)
  
  (setq *layoutname_list* layoutname_list_backup)
  (makedsd dirpath dwgname_list_3 "-Layout1_2.pdf" "PUBLIST_3.dsd")
  (while dwgname_list_3
    (setq dwgname (car dwgname_list_3))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (vla-StartUndoMark doc)
    
    (if (and (member dwgname rebar_file2) (member dwgname text_file2) (member dwgname pointer_file2))
      (progn
        (setq text_file_index2 (vl-position dwgname text_file2))
        (setq rebar_file_index2 (vl-position dwgname rebar_file2))
        (setq pointer_file_index2 (vl-position dwgname pointer_file2))
        
        (turnon_alllayer doc )
      )
    )
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq dwgname_list_3 (cdr dwgname_list_3))
  )
  (command "-Publish" (strcat dirpath "\\" "PUBLIST_3.dsd") )
)
;------------------------------------------LINE INFO EXTRACTION------------------------------------------
(defun extractlineinfo ( doc dwgname target_layer_name / lst1 lst2)
  (setq lst1 '())
  (setq lst2 '())
  (setq ss (vla-get-modelspace doc ))
  (while target_layer_name
    (vlax-for obj ss
      (setq x (vlax-vla-object->ename obj))
      (if 
        (and
        (eq (vla-get-objectname obj) "AcDbLine")
        (= (vla-get-layer obj) (car target_layer_name))
        )
        (progn
        (setq ep (cdr (assoc 11 (entget x))))
        (setq sp (cdr (assoc 10 (entget x))))
        (setq len (vla-get-length obj))
        (setq lay (vla-get-layer obj))
        (setq lst2 (cons ep lst2))
        (setq lst2 (cons sp lst2))
        (setq lst2 (cons len lst2))
        (setq lst2 (cons lay lst2))
        (setq lst2 (cons x lst2))
        (setq lst2 (cons dwgname lst2))
        (setq lst1 (cons lst2 lst1))
        (setq lst2 '())
        )
      )
      (if 
        (and
        (eq (vla-get-objectname obj) "AcDbPolyline")
        (= (vla-get-layer obj) (car target_layer_name))
        )
        (progn
        (setq pa (+ (vlax-curve-getEndParam x) 1))
        (setq lst nil) ; Initialize an empty list to store the points
        (while (setq pt (vlax-curve-getPointAtParam x (setq pa (- pa 1))))
          (setq lst (cons pt lst)))
        (setq edges-lst (mapcar 'list lst (cdr lst))) ; Group consecutive points into edges
        (setq edges-lst (reverse edges-lst)) ; Reverse the list to maintain the correct order

        ;; Create formatted list of edges
        (setq formatted-edges '())
        (setq entity-counter 1) ; Initialize the entity counter to 1
        (setq entity-name (substr (vl-princ-to-string x) 1 (- (strlen (vl-princ-to-string x)) 1)))
        (foreach edge edges-lst
          (setq formatted-edge
                (list
                dwgname ; [0] File Name
                (strcat entity-name (itoa entity-counter) ">") ; [1] Entity Name
                (strcase (cdr (assoc 8 (entget x)))) ; [2] Layer Name
                (distance (car edge) (cadr edge)) ; [3] Line Length
                (car edge) ; [4] Start Coord
                (cadr edge) ; [5] End Coord
                ))
          (setq entity-counter (+ entity-counter 1))
          (setq formatted-edges (cons formatted-edge formatted-edges))
        )
        (setq lst1 (append lst1 formatted-edges))
        )
      )
    )
    (setq target_layer_name (cdr target_layer_name))
  )
  (setq lst1 lst1)
)
(defun extracttextinfo ( doc dwgname target_layer_name / lst1 lst2)
  (setq lst1 '())
  (setq lst2 '())
  (setq ss (vla-get-modelspace doc ))
  (vlax-for obj ss
    (setq x (vlax-vla-object->ename obj))
    (if 
      (and
        (or
          (eq (vla-get-objectname obj) "AcDbMText")
          (eq (vla-get-objectname obj) "AcDbText")
        )
        (not (eq (cdr (assoc 1 (entget x))) ""))
      )
      (progn
        (setq lst2 (cons (cdr (assoc 1 (entget x))) lst2)) ;Text
        (setq lst2 (cons (cdr (assoc 41 (entget x))) lst2));Width
        (setq lst2 (cons (cdr (assoc 40 (entget x))) lst2));Height
        (setq lst2 (cons (cdr (assoc 10 (entget x))) lst2));Midpoint
        (setq lst2 (cons (cdr (assoc 50 (entget x))) lst2));Rotation
        (setq lst2 (cons (vla-get-objectname obj) lst2))
        (setq lst2 (cons x lst2))
        (setq lst2 (cons dwgname lst2))
        (setq lst1 (cons lst2 lst1))
        (setq lst2 '())
      )
    )
    (if 
      (and
        (eq (vla-get-objectname obj) "AcDbRotatedDimension")
        (not (eq (cdr (assoc 1 (entget x))) ""))
      )
      (progn
        (setq lst2 (cons (cdr (assoc 1 (entget x))) lst2))  ;
        (setq lst2 (cons (cdr (assoc 13 (entget x))) lst2)) ;
        (setq lst2 (cons (cdr (assoc 11 (entget x))) lst2)) ;
        (setq lst2 (cons (cdr (assoc 10 (entget x))) lst2)) ;
        (setq lst2 (cons (cdr (assoc 50 (entget x))) lst2)) ;
        (setq lst2 (cons (vla-get-objectname obj) lst2))
        (setq lst2 (cons x lst2))
        (setq lst2 (cons dwgname lst2))
        (setq lst1 (cons lst2 lst1))
        (setq lst2 '())
      )
    )
  )
  (setq lst1 (reverse lst1))
)

;----------------------------------------------FILTER LAYER----------------------------------------------
(defun filterlayer (doc target_layer / layertable layer)
  (setq layertable (vla-get-layers doc))
  (vlax-for layer layertable
    (if (member (vla-get-Name layer) target_layer)
      (progn
        ; (vla-put-plottable layer :vlax-true)  ; 設置圖層為可打印
        (vla-put-LayerOn layer :vlax-true)  ; 設置圖層為可打印
        (princ (strcat "圖層名稱: " (vla-get-Name layer) "\n"))  ; 印出圖層名稱
      )
      (progn
        (vla-put-LayerOn layer :vlax-false) 
        ; (vla-put-plottable layer :vlax-false)  ; 設置圖層為不可打印
        (princ (vla-get-Name layer))
      )
    )
  )
)

(defun turnon_alllayer (doc / layertable layer)
  (setq layertable (vla-get-layers doc))
  (vlax-for layer layertable
      (vla-put-plottable layer :vlax-true)
  )
)
;----------------------------------------------MAKE DSD----------------------------------------------
(defun set-layout-plotter-config (doc layout-name config-name)
  (setq layouts (vla-get-Layouts doc))
  (setq layout (vla-Item layouts layout-name))
  (if (or (equal (vla-get-configname layout) "None") (equal (vla-get-configname layout) "無"))
    (progn
    (vla-put-ConfigName layout config-name) ;config-name = AutoCAD PDF (General Documentation).pc3
    (vla-put-CanonicalMediaName layout "ISO_full_bleed_A3_(297.00_x_420.00_MM)") ;paper size
    (prompt (strcat "\nThe plotter configuration for layout '" layout-name "' has been set to '" config-name "'."))
    )
  )
)

(defun makedsd (dirpath dwgname_list pdfname dsdname / file)
  
  ;;;(setq layouts_to_plot (dos_multilist "Create Multi-sheet DWF file" "Select drawings" (layoutlist)))
  (setq NumTabs (length layouts_to_plot));Number of tabs selected
  (setq pathtxt (strcat dirpath "\\" dsdname))
  (setq file (open (strcat dirpath "\\" dsdname) "w"))
    
  (write-line "[DWF6Version]" file)
  (write-line  "Ver=1" file)
  (write-line  "[DWF6MinorVersion]" file)
  (write-line  "MinorVer=1" file)
  
  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (write-line (strcat "[DWF6Sheet:" (substr dwgname 1 (- (strlen dwgname) 4)) "-Layout1]")file)
    (write-line (strcat "DWG=" dirpath "\\" dwgname)file)
    (write-line (strcat "Layout=" (car *layoutname_list*) )file)
    (write-line (strcat "Setup=" ) file)
    (write-line (strcat "OriginalSheetPath=" dirpath "\\" dwgname )file)
    (write-line (strcat "Has Plot Port=1" )file)
    (setq dwgname_list (cdr dwgname_list))
    (setq *layoutname_list* (cdr *layoutname_list*))
  )
  
  (write-line (strcat "[Target]") file)
  (write-line (strcat "Type=6" ) file)
  (write-line (strcat "DWF=" dirpath "\\" pdfname) file)
  (write-line (strcat "OUT="dirpath "\\" ) file)
  (write-line (strcat "PWD=" )file)
    
  (write-line (strcat "[PdfOptions]" )file)
  (write-line (strcat "IncludeHyperlinks=TRUE" )file)
  (write-line (strcat "CreateBookmarks=TRUE" )file)
  (write-line (strcat "CaptureFontsInDrawing=TRUE" )file)
  (write-line (strcat "ConvertTextToGeometry=FALSE" )file)
  (write-line (strcat "VectorResolution=1200" )file)
  (write-line (strcat "RasterResolution=400" )file)
  (write-line (strcat "[AutoCAD Block Data]" )file)
  (write-line (strcat "IncludeBlockInfo=0" )file)
  (write-line (strcat "BlockTmplFilePath=" )file)
  (write-line (strcat "[SheetSet Properties]" )file)
  (write-line (strcat "IsSheetSet=FALSE" )file)
  (write-line (strcat "IsHomogeneous=FALSE" )file)
  (write-line (strcat "SheetSet Name=" )file)
  (write-line (strcat "NoOfCopies=1" )file)
  (write-line (strcat "PlotStampOn=FALSE" )file)
  (write-line (strcat "ViewFile=FALSE" )file)
  (write-line (strcat "JobID=0" )file)
  (write-line (strcat "SelectionSetName=" )file)
  (write-line (strcat "AcadProfile=" )file)
  (write-line (strcat "CategoryName=" )file)
  (write-line (strcat "LogFilePath=" )file)
  (write-line (strcat "IncludeLayer=TRUE" )file)
  (write-line (strcat "LineMerge=FALSE" )file)
  (write-line (strcat "CurrentPrecision=" )file)
  (write-line (strcat "PromptForDwfName=TRUE" )file)
  (write-line (strcat "PwdProtectPublishedDWF=FALSE" )file)
  (write-line (strcat "PromptForPwd=FALSE" )file)
  (write-line (strcat "RepublishingMarkups=FALSE" )file)
  (write-line (strcat "PublishSheetSetMetadata=FALSE" )file)
  (write-line (strcat "PublishSheetMetadata=FALSE" )file)
  (write-line (strcat "3DDWFOptions=0" )file)

  (close file)
  (princ)
)

;------------------------------------------EXPORT TO CSV FUNCTIONS------------------------------------------
(defun _writecsv (method fn lst / f)
    (cond ((and (eq 'str (type fn)) (setq f (open fn method)))
	   (foreach x lst
	     (if (= 'list (type x))
	       (write-line
		 (apply 'strcat (mapcar '(lambda (z) (strcat (vl-princ-to-string z) ",")) x))
		 f
	       )
	       (vl-princ-to-string x)
	     )
	   )
	   (close f)
	   fn
	  )
  )
)
;------------------------------------------MAIN CODE TO BE RUNNING------------------------------------------
(vl-load-com)
(princ "Hello, this is the main code to be running")
(setq oldpath (getvar "dwgprefix")) 
(princ oldpath)
(setq wtype (wtype_selection))
(setq dtype (dtype_selection))
(setq cur_doc (vla-get-ActiveDocument (vlax-get-acad-object)))
(setq OldFda (getvar "FILEDIA"))
(command "FILEDIA" 0)
(setq OldBgp (getvar "BACKGROUNDPLOT"))
(command "BACKGROUNDPLOT" 0)
(setq OldLayEva (getvar "LAYEREVALCTL"))
(command "LAYEREVALCTL" 0)

; ------------------------------------------------------ For Diaphragm ------------------------------------------------------
(if (and (= dtype "Plan Drawings") (= wtype "Diaphragm"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the DIAPHRAGM WALL " (vl-princ-to-string dtype) " folder: ") 
                (getvar "dwgprefix")
              )) ;or write (getvar "dwgprefix")
    (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1)) 
    (setq target_file (vl-directory-files dirpath "*.dwg" 1))
    (setq *layoutname_list* '())
    (setq target_layer (preloop dirpath dwgname_list))
    (setq target_layer_0 (nth 0 target_layer))
    (setq target_layer_1 (nth 1 target_layer))
    (setq target_file (vl-remove-if ''( (item) (not (or (member item target_layer_0) (member item target_layer_1)))) target_file))
    (mainloop1 dirpath target_file target_layer)
    (startapp "dist\\Data Process - Plan Drawings.exe" dirpath)
  ))
(if (and (= dtype "Elevation Drawings") (= wtype "Diaphragm"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the DIAPHRAGM WALL " (vl-princ-to-string dtype) " folder: ") 
                (getvar "dwgprefix")
              )) ;or write (getvar "dwgprefix")
    (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1))
    (setq target_file (vl-directory-files dirpath "*.dwg" 1))
    (setq *layoutname_list* '())
    (setq target_layer (preloop dirpath dwgname_list))
    (setq target_layer_0 (nth 0 target_layer))
    (setq target_layer_1 (nth 1 target_layer))
    (setq target_file (vl-remove-if ''( (item) (not (or (member item target_layer_0) (member item target_layer_1)))) target_file))
    (mainloop2 dirpath target_file target_layer)
    (startapp "dist\\Data Process - Elevation Drawings.exe" dirpath)
  ))
; if dynamic type is Structural Descriptions and wtype is Diaphragm
(if (and (= dtype "Structural Descriptions")(= wtype "Diaphragm"))
  (progn
    (command "BACKGROUNDPLOT" 2)
    (setq *temp* (getfiled (strcat "Select the DIAPHRAGM WALL " (vl-princ-to-string dtype) " folder") "" "dwg" 8))
    (setq filepath *temp*)
    (setq filepath2 *temp*)
    (setq dirpath (substr *temp* 1 (vl-string-position (ascii "\\") *temp* nil t)))
    (setq filename (list (vl-string-left-trim dirpath *temp*)))
    (setq *layoutname_list* '())
    (mainloop3 filepath dirpath filename)
    (command "BACKGROUNDPLOT" 0)
    (startapp "dist\\Data Process - Structural Descriptions.exe" dirpath)
  ))
(if (and (= dtype "Rebar Drawings") (= wtype "Diaphragm"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the DIAPHRAGM WALL " (vl-princ-to-string dtype) " folder: ") 
                (getvar "dwgprefix")
              )) ;or write (getvar "dwgprefix")
    (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1)) 
    (setq target_file (vl-directory-files dirpath "*.dwg" 1))
    (setq *layoutname_list* '())
    (setq target_layer_big (preloop4 dirpath dwgname_list))
    (setq target_layer_small_1 (nth 0 target_layer_big))
    (setq target_layer_small_2 (nth 1 target_layer_big))
    (setq target_layer_0 (nth 0 target_layer_small_1))
    (setq target_layer_1 (nth 1 target_layer_small_1))
    (setq target_layer_2 (nth 2 target_layer_small_1))
    (setq target_layer_3 (nth 0 target_layer_small_2))
    (setq target_layer_4 (nth 1 target_layer_small_2))
    (setq target_layer_5 (nth 2 target_layer_small_2))
    (setq target_file (vl-remove-if ''( (item) (not (or (member item target_layer_0) (member item target_layer_1) (member item target_layer_2) (member item target_layer_3) (member item target_layer_4) (member item target_layer_5)))) target_file))
    (mainloop4 dirpath target_file target_file target_layer_small_1 target_layer_small_2)
    (startapp "dist\\Data Process - Rebar Drawings.exe" dirpath)
  ))

; ------------------------------------------------For Sheet Pile ------------------------------------------------------
; 鋼板樁平面圖
(if (and (= dtype "Plan Drawings") (= wtype "SheetPile"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the DIAPHRAGM WALL " (vl-princ-to-string dtype) " folder: ") 
                (getvar "dwgprefix")
              )) ;or write (getvar "dwgprefix")
    (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1)) 
    (setq target_file (vl-directory-files dirpath "*.dwg" 1))
    (setq *layoutname_list* '())
    (setq target_layer (preloop_for_selectlayer_folder dirpath dwgname_list))
    (princ target_layer)
    (setq wall_file (nth 0 target_layer))
    (setq text_file (nth 1 target_layer))
    (setq wall_layer (nth 2 target_layer))
    (setq text_layer (nth 3 target_layer))
    (setq layoutname_list_backup *layoutname_list*)
    (publish_bylayer_folder dirpath dwgname_list text_layer "-Layout1.pdf" "PUBLIST.dsd") 
    (setq *layoutname_list* layoutname_list_backup)
    (publish_bylayer_folder dirpath dwgname_list wall_layer "-Layout2.pdf" "PUBLIST_2.dsd")
    (setq command (strcat "dist\\main.exe -t SheetPile -d plan -p " dirpath "\\-Layout1.pdf -p2 " dirpath "\\-Layout2.pdf"))
    (startapp command)
  )
)

; 鋼板樁立面圖
(if (and (= dtype "Elevation Drawings") (= wtype "SheetPile"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the Sheet Pile " (vl-princ-to-string dtype) " folder: ") 
                (getvar "dwgprefix")
              ))
    (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1)) 
    (setq target_file (vl-directory-files dirpath "*.dwg" 1))
    (setq *layoutname_list* '())
    (preloopp_for_all_folder dirpath dwgname_list)
    (publish_all_folder dirpath dwgname_list)
    (setq command (strcat "dist\\main.exe -t SheetPile -d eval -p " dirpath "\\-Layout1.pdf"))
    (startapp command)
  )
)

; 鋼板樁鋼筋圖
(if (and (= dtype "Rebar Drawings") (= wtype "SheetPile"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the Sheet Pile " (vl-princ-to-string dtype) " folder: ") 
                (getvar "dwgprefix")
              ))
    (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1)) 
    (setq target_file (vl-directory-files dirpath "*.dwg" 1))
    (setq *layoutname_list* '())
    (preloopp_for_all_folder dirpath dwgname_list)
    (publish_all_folder dirpath dwgname_list)
    (setq command (strcat "dist\\main.exe -t SheetPile -d rebar -p " dirpath "\\-Layout1.pdf"))
    (startapp command)
  )
)

(command "FILEDIA" OldFda)
(command "BACKGROUNDPLOT" OldBgp)
(command "LAYEREVALCTL" OldLayEva)
(princ "Extraction Complete")
(princ)
