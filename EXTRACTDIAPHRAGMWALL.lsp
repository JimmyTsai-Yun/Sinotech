(load "utils.lsp")
;------------------------------------------LOOP EVERY FILES------------------------------------------

; 鋼板樁平面圖、排樁平面圖 UI函數(舊版)
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

; 鋼板樁立面、配筋，排樁配筋 UI、處理函數
(defun preloopp_for_all_folder (dirpath dwgname_list)
  (setq full_text_lst '(("FileName" "EntityName" "ObjectType" "RotationAngle" "CentreCoor" "Height" "Width" "Text")))
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
    (setq ss (vla-get-modelspace doc))
    (setq lst_temp '())
    (setq lst_temp1 '())
    (vlax-for obj ss
      (setq x (vlax-vla-object->ename obj))
      (if (eq (vla-get-objectname obj) "AcDbText")
        (progn
          (setq lst_temp (cons (cdr (assoc 1 (entget x))) lst_temp))
          (setq lst_temp (cons (cdr (assoc 41 (entget x))) lst_temp))
          (setq lst_temp (cons (cdr (assoc 40 (entget x))) lst_temp))
          (setq CentreCoor (cdr (assoc 10 (entget x))))
            (foreach num CentreCoor
              (setq num_str (rtos num 2 2))
              (setq CentreCoor (subst num_str num CentreCoor))
          )
          (setq lst_temp (cons CentreCoor lst_temp))
          (setq lst_temp (cons (cdr (assoc 50 (entget x))) lst_temp))
          (setq lst_temp (cons (vla-get-objectname obj) lst_temp))
          (setq lst_temp (cons x lst_temp))
          (setq lst_temp (cons dwgname lst_temp))
          (setq lst_temp1 (cons lst_temp lst_temp1))
          (setq lst_temp '())
        )
      )
    )
    (setq lst_temp1 lst_temp1)
    (setq full_text_lst (append full_text_lst lst_temp1))
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq dwgname_list (cdr dwgname_list))
  )
  (_writecsv "W" (strcat dirpath "\\FullText.csv") full_text_lst)
)

(defun preloop_for_plan_eval_drawing(dirpath dwgname_list / wall_file wall_layer)
  (setq collectedlayer '()) ; 每張圖為一單位，存放圖的圖層名稱
  (setq collectedlayer_file '()) ; 存放圖檔名稱
  (setq dwgname_list_shown dwgname_list)
  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
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
  (setq dcl_id (load_dialog "dcl\\plan_selection.dcl")) ; change directory path to known location
  (if (not (new_dialog "plan_selection" dcl_id))
  (exit)
  )

  ; 初始化 source file， 並設定 action_tile
  (start_list "source_file")
  (foreach itm dwgname_list_shown (add_list itm))
  (end_list)
  (action_tile "source_file" 
    (vl-prin1-to-string
      '(progn
        (setq selected_source_file_index (atoi (get_tile "source_file")))
        (start_list "source_layer")
        (foreach itm (nth selected_source_file_index collectedlayer) (add_list itm))
        (end_list)
        (set_tile "source_layer" "0")
        (set_tile "source_layer_slider" "0")
      )
    )
  )

  ; 初始化 all layer， 並設定 action_tile
  (start_list "source_layer")
  (foreach itm '() (add_list itm))
  (end_list)
  (action_tile "source_layer" "")

  ; 初始化 selected file， 並設定 action_tile
  (action_tile "selected_file" 
    (vl-prin1-to-string
      '(progn
        (setq added_index (atoi (get_tile "selected_file")))
        (start_list "selected_layer")
        (foreach itm (nth added_index wall_layer) (add_list itm))
        (end_list)
        (set_tile "selected_layer_slider" "0")
      )
    )
  )

  (action_tile "add_layer"
    (vl-prin1-to-string
          '(progn
            (setq selected_source_file_index (atoi (get_tile "source_file")))
            (setq selected_filename (nth selected_source_file_index dwgname_list_shown))
            (if (boundp 'wall_file)
              (progn
                (if (not (member selected_filename wall_file))
                  (progn
                  (setq wall_file (append wall_file (list selected_filename)))
                  (setq wall_layer (append wall_layer (list'())))
                  )
                )
              )
              (progn
                (setq wall_file (list selected_filename))
                (setq wall_layer (list'()))
              ))
            (start_list "selected_file")
              (foreach itm wall_file (add_list itm))
            (end_list)
            (setq added_source_file_index (vl-position selected_filename wall_file))
            (set_tile "selected_file" (vl-princ-to-string added_source_file_index))
            
            (setq temp_collectedlayer_wall  (nth selected_source_file_index collectedlayer_wall)) ; 獲取選中的圖的圖層名稱，等一下要透過扣除被選中的圖層名稱進行更新
            (setq temp_wall_layer  (nth added_source_file_index wall_layer)) ; 獲取選中的圖的在記錄中的圖層名稱(空列表)，等一下要透過新增被選中的圖層名稱進行更新
            (mapcar 'dclist '("source_layer" "selected_layer") ; 更新 source_layer 和 selected_layer 的顯示內容              <---\
                (mapcar 'set '(temp_collectedlayer_wall temp_wall_layer) ; 更新 temp_collectedlayer_wall 和 temp_wall_layer  ---/
                    (shiftitems (read (strcat "(" (get_tile "source_layer") ")")) temp_collectedlayer_wall temp_wall_layer)
                ))
            (set_tile "source_layer_slider" "0")
            (set_tile "selected_file_slider" "0")
            (set_tile "selected_layer_slider" "0")
            (setq collectedlayer_wall (SubstNth temp_collectedlayer_wall selected_source_file_index collectedlayer_wall)) ; 將 temp_collectedlayer_wall 更新到 collectedlayer_wall
            (setq wall_layer (SubstNth temp_wall_layer added_source_file_index wall_layer)) ; 將 temp_wall_layer 更新到 wall_layer
            )))

  (action_tile "remove_layer"
    (vl-prin1-to-string
      '(progn
        (setq selected_remove_file_index (atoi (get_tile "selected_file")))
        (setq selected_remove_filename (nth selected_remove_file_index wall_file))
        (setq selected_file_index (vl-position selected_remove_filename dwgname_list_shown))
        (setq temp_collectedlayer_wall  (nth selected_file_index collectedlayer_wall))
        (setq temp_wall_layer  (nth selected_remove_file_index wall_layer))
        (mapcar 'dclist '("selected_layer" "source_layer")
          (mapcar 'set '(temp_wall_layer temp_collectedlayer_wall)
              (shiftitems  (read (strcat "(" (get_tile "selected_layer") ")")) temp_wall_layer temp_collectedlayer_wall)
          ))
        (setq collectedlayer_wall (SubstNth temp_collectedlayer_wall selected_file_index collectedlayer_wall))
        (setq wall_layer (SubstNth temp_wall_layer selected_remove_file_index wall_layer))
        
        (set_tile "source_layer" (itoa (vl-position selected_remove_filename dwgname_list_shown)))
        (set_tile "source_layer_slider" "0")
        (set_tile "selected_layer_slider" "0")
        
        (if (null temp_wall_layer)
          (progn
            (setq wall_file (RemoveNth selected_remove_file_index wall_file))
            (setq wall_layer (RemoveNth selected_remove_file_index wall_layer))
            (start_list "selected_file")
            (foreach itm wall_file (add_list itm))
            (end_list)
            (set_tile "selected_file_slider" "0")
          ))
        )))
  (action_tile "source_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_file_slider" "source_file" dwgname_list_shown 3 "   ")))
  (action_tile "source_layer_slider" (vl-prin1-to-string '(slider_cut_restore_string "source_layer_slider" "source_layer" (nth (atoi (get_tile "source_file")) collectedlayer_wall) 3 "   ")))
  (action_tile "selected_file_slider" (vl-prin1-to-string '(slider_cut_restore_string "selected_file_slider" "selected_file" wall_file 3 "   ")))
  (action_tile "selected_layer_slider" (vl-prin1-to-string '(if (not (equal wall_file nil))
      (slider_cut_restore_string "selected_file_slider" "selected_file" (nth (atoi (get_tile "selected_file")) wall_layer) 3 "   "))
      ))

  (action_tile "accept"
  (vl-prin1-to-string
          '(progn
            (done_dialog)
  )))
  
  (action_tile "cancel"
  (strcat
  "(quit)"
  ))
  (start_dialog)
  (unload_dialog dcl_id)
  (setq target_layer (list wall_file wall_layer))
)

; 連續壁平面、立面圖 UI函數(舊版)
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
    
  ; 初始化 source wall， 並設定 action_tile 
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

; 連續壁配筋圖 UI函數(舊版)(不會更動)
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

; 連續壁平面圖 處理函數(舊版)
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

; 連續壁立面圖 處理函數(舊版)
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

; 結構一般說明 處理函數
(defun mainloop3 (dirpath dwgname_list)
  (setq full_text_lst '(("FileName" "EntityName" "ObjectType" "RotationAngle" "CentreCoor" "Height" "Width" "Text")))
  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (vla-StartUndoMark doc) 
    (setq ss (vla-get-modelspace doc))
    (setq lst_temp '())
    (setq lst_temp1 '())
    (vlax-for obj ss
      (setq x (vlax-vla-object->ename obj))
      (if (or (eq (vla-get-objectname obj) "AcDbText")
              (eq (vla-get-objectname obj) "AcDbMText"))
        (progn
          (setq lst_temp (cons (cdr (assoc 1 (entget x))) lst_temp))
          (setq lst_temp (cons (cdr (assoc 41 (entget x))) lst_temp))
          (setq lst_temp (cons (cdr (assoc 40 (entget x))) lst_temp))
          (setq CentreCoor (cdr (assoc 10 (entget x))))
          (foreach num CentreCoor
            (setq num_str (rtos num 2 2))
            (setq CentreCoor (subst num_str num CentreCoor))
          )
          (setq lst_temp (cons CentreCoor lst_temp))
          (setq lst_temp (cons (cdr (assoc 50 (entget x))) lst_temp))
          (setq lst_temp (cons (vla-get-objectname obj) lst_temp))
          (setq lst_temp (cons x lst_temp))
          (setq lst_temp (cons dwgname lst_temp))
          (setq lst_temp1 (cons lst_temp lst_temp1))
          (setq lst_temp '())
        )
      )
    )
    (setq lst_temp1 lst_temp1)
    (setq full_text_lst (append full_text_lst lst_temp1))
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq dwgname_list (cdr dwgname_list))
  )
  (_writecsv "W" (strcat dirpath "\\FullText.csv") full_text_lst)
)

; (defun mainloop3 (filepath dirpath filename)
;   (vl-load-com)
;   (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) *temp*))
;   (setq full_text_lst '(("FileName" "EntityName" "ObjectType" "RotationAngle" "CentreCoor" "Height" "Width" "Text")))
;   (vla-StartUndoMark doc)
;   (setq ss (vla-get-modelspace doc))
;   (setq lst_temp '())
;   (setq lst_temp1 '())
;   (vlax-for obj ss
;     (setq x (vlax-vla-object->ename obj))
;     (if (eq (vla-get-objectname obj) "AcDbText")
;       (progn
;         (setq lst_temp (cons (cdr (assoc 1 (entget x))) lst_temp))
;         (setq lst_temp (cons (cdr (assoc 41 (entget x))) lst_temp))
;         (setq lst_temp (cons (cdr (assoc 40 (entget x))) lst_temp))
;         (setq CentreCoor (cdr (assoc 10 (entget x))))
;           (foreach num CentreCoor
;             (setq num_str (rtos num 2 2))
;             (setq CentreCoor (subst num_str num CentreCoor))
;         )
;         (setq lst_temp (cons CentreCoor lst_temp))
;         (setq lst_temp (cons (cdr (assoc 50 (entget x))) lst_temp))
;         (setq lst_temp (cons (vla-get-objectname obj) lst_temp))
;         (setq lst_temp (cons x lst_temp))
;         (setq lst_temp (cons dwgname lst_temp))
;         (setq lst_temp1 (cons lst_temp lst_temp1))
;         (setq lst_temp '())
;       )
;     )
;   )
;   (setq lst_temp1 lst_temp1)
;   (setq full_text_lst (append full_text_lst lst_temp1))
;   (_writecsv "W" (strcat dirpath "\\FullText.csv") full_text_lst)
  
;   (vla-purgeall doc)
;   (vla-EndUndoMark doc)
;   (vla-save doc)
;   (vla-close doc)
; )

; 連續壁配筋圖 處理函數
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
  (setq full_text_lst '(("FileName" "EntityName" "ObjectType" "RotationAngle" "CentreCoor" "Height" "Width" "Text")))
  (setq line_lst2 '(("FileName" "EntityName" "Layer" "Length" "StartCoor" "EndCoor")))
  (setq helper_lst2 '(("FileName" "EntityName" "ObjectType" "BasePoint" "UpLeftPoint" "DownRightPoint")))
  
  (setq layoutname_list_backup *layoutname_list*)
  ;(makedsd dirpath dwgname_list "-Layout1.pdf" "PUBLIST.dsd")
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
  ;(command "-Publish" (strcat dirpath "\\" "PUBLIST.dsd") )
  (_writecsv "W" (strcat dirpath "\\helper_line.csv") helper_lst)
  (_writecsv "W" (strcat dirpath "\\vertical_line.csv") line_lst)
  ; (_writecsv "W" (strcat dirpath "\\Text Info.csv") text_lst)
  
  (setq *layoutname_list* layoutname_list_backup)
  ;(makedsd dirpath dwgname_list_2 "-Layout1_2_ref.pdf" "PUBLIST_2.dsd")
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
        (setq lst_temp '())
        (setq lst_temp1 '())
        (setq ss (vla-get-modelspace doc ))
        (vlax-for obj ss
          (setq x (vlax-vla-object->ename obj))

          (if (eq (vla-get-objectname obj) "AcDbText")
             (progn
              (setq lst_temp (cons (cdr (assoc 1 (entget x))) lst_temp))
              (setq lst_temp (cons (cdr (assoc 41 (entget x))) lst_temp))
              (setq lst_temp (cons (cdr (assoc 40 (entget x))) lst_temp))
              (setq CentreCoor (cdr (assoc 10 (entget x))))
                (foreach num CentreCoor
                  (setq num_str (rtos num 2 2))
                  (setq CentreCoor (subst num_str num CentreCoor))
              )
              (setq lst_temp (cons CentreCoor lst_temp))
              (setq lst_temp (cons (cdr (assoc 50 (entget x))) lst_temp))
              (setq lst_temp (cons (vla-get-objectname obj) lst_temp))
              (setq lst_temp (cons x lst_temp))
              (setq lst_temp (cons dwgname lst_temp))
              (setq lst_temp1 (cons lst_temp lst_temp1))
              (setq lst_temp '())
            )
          )

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
        (setq lst_temp1 lst_temp1)
        (setq full_text_lst (append full_text_lst lst_temp1))
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
  
  ;(command "-Publish" (strcat dirpath "\\" "PUBLIST_2.dsd") )
  (_writecsv "W" (strcat dirpath "\\FullText.csv") full_text_lst)
  ; (_writecsv "W" (strcat dirpath "\\SH Text Info.csv") text_lst2)
  ; (_writecsv "W" (strcat dirpath "\\SH Line Info.csv") line_lst2)
  (_writecsv "W" (strcat dirpath "\\Sh_helper.csv") helper_lst2)
  
  (setq *layoutname_list* layoutname_list_backup)
  ;(makedsd dirpath dwgname_list_3 "-Layout1_2.pdf" "PUBLIST_3.dsd")
  ; (while dwgname_list_3
  ;   (setq dwgname (car dwgname_list_3))
  ;   (vl-load-com)
  ;   (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
  ;   (vla-StartUndoMark doc)
    
  ;   (if (and (member dwgname rebar_file2) (member dwgname text_file2) (member dwgname pointer_file2))
  ;     (progn
  ;       (setq text_file_index2 (vl-position dwgname text_file2))
  ;       (setq rebar_file_index2 (vl-position dwgname rebar_file2))
  ;       (setq pointer_file_index2 (vl-position dwgname pointer_file2))
        
  ;       (turnon_alllayer doc )
  ;     )
  ;   )
  ;   (vla-purgeall doc)
  ;   (vla-EndUndoMark doc)
  ;   (vla-save doc)
  ;   (vla-close doc)
  ;   (setq dwgname_list_3 (cdr dwgname_list_3))
  ; )
  ;(command "-Publish" (strcat dirpath "\\" "PUBLIST_3.dsd") )
)

(defun mainloop_for_Dia_plan_eval (dirpath dwgname_list target_layer)
  (setq wall_file (nth 0 target_layer)) ; 範例 (0 1 2 3 4 5)
  (setq wall_layer (nth 1 target_layer)) ; 範例 ((s1, s2, s3) (s4, s5, s6))
  ;; 初始化一個空列表來存儲符合條件的聚合線頂點，並初始化CSV標題
  (setq full_list '(("FileName" "EntityName" "Layer" "ID" "Bulge" "X" "Y")))

  (princ "\nStart to extract data from drawings...")

  (while wall_file
    (setq dwgname (car wall_file))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (vla-StartUndoMark doc)
    (setq ss (vla-get-modelspace doc))

    (setq wall_layer_index (vl-position dwgname wall_file))
    (setq wall_layer_name_list (nth wall_layer_index wall_layer)) ;(s1, s2, s3)

    ;; 初始化 ID 計數器
    (setq id_counter 1)

    (princ (strcat "\nProcessing " dwgname "..."))
    (princ wall_layer_name_list)

    (vlax-for obj ss 
      (setq x (vlax-vla-object->ename obj)) ; 獲取圖元名稱
      (setq obj_name (vla-get-objectname obj)) ; 獲取物件名稱
      (setq obj_layer (vla-get-layer obj)) ; 獲取物件的圖層名稱
      
      ;; 如果物件是聚合線且圖層為"TYPE_S1"
      ;; 遍歷多段線的頂點
      (if (and (eq obj_name "AcDbPolyline") (member obj_layer wall_layer_name_list))
        (progn
          ;; 打印物件名稱和圖層
          ; (princ (strcat "\nObject Name: " obj_name)) 
          ; (princ (strcat "\n  Layer: " obj_layer))
          (setq polyData (entget (vlax-vla-object->ename obj))) ; 獲取多段線的資料列表

          ; ;; 檢查是否閉合
          ; (setq isClosed (if (= (logand 1 (cdr (assoc 70 polyData))) 1) "Yes" "No"))
          ; (princ (strcat "\nClosed: " isClosed))

          (foreach dataItem polyData
            (setq single_row_list '())
            (if (= (car dataItem) 10) ; 頂點座標
              (progn
                (setq x (rtos (cadr dataItem) 2 4))
                (setq y (rtos (caddr dataItem) 2 4))
                ; (princ (strcat "\nVertex " ": (" x ", " y ")"))
                (if (= (car dataItem) 42) ; 彎曲度
                  (setq bulge (rtos (cdr dataItem) 2 4))
                )
                (setq single_row_list (list (strcase (vla-get-name doc)) obj_name obj_layer (itoa id_counter) bulge x y))
                (setq full_list (append full_list (list single_row_list)))
              )
            )
          )
          ; 增加引數
          (setq id_counter (1+ id_counter))
        )
      )
    )
    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq wall_file (cdr wall_file))
    (setq wall_layer (cdr wall_layer))
    (princ "\nDone.")
  )
  (_writecsv "W" (strcat dirpath "\\LineInfo.csv") full_list)
)

(defun output_pile_info(dirpath dwgname_list target_layer)
  (setq wall_file (nth 0 target_layer))
  (setq text_file (nth 1 target_layer))
  (setq wall_layer (nth 2 target_layer))
  (setq text_layer (nth 3 target_layer))
  (setq pile_lst '(("x_coor" "y_coor")))

  (while dwgname_list
    (setq dwgname (car dwgname_list))
    (vl-load-com)
    (setq doc (vla-Open (vla-get-documents (vlax-get-acad-object)) (strcat dirpath "\\" dwgname)))
    (vla-StartUndoMark doc)

    (if (and (member dwgname wall_file) (member dwgname text_file))
      (progn
        (setq wall_file_index (vl-position dwgname wall_file))
        (setq pile_lst (append pile_lst (extractpileinfo doc dwgname (nth wall_file_index wall_layer))))
      )
    )

    (vla-purgeall doc)
    (vla-EndUndoMark doc)
    (vla-save doc)
    (vla-close doc)
    (setq dwgname_list (cdr dwgname_list))
  )
  (_writecsv "W" (strcat dirpath "\\pile.csv") pile_lst)
)
;------------------------------------------DATA INFO EXTRACTION------------------------------------------
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
(defun extractpileinfo(doc dwgname target_layer_name / obj atts att)
  (setq lst1 '())
  (setq lst2 '())
  (setq ss (vla-get-modelspace doc))
  (while target_layer_name
    (vlax-for obj ss 
      (setq x (vlax-vla-object->ename obj))
      ; (princ (strcat "val-get-layer" (vla-get-layer obj)))
      ; (princ "\n")
      (if 
        (and
        (= (vla-get-layer obj) (car target_layer_name))
        (eq (vla-get-objectname obj) "AcDbBlockReference")  ; 檢查對象是否為圖塊引用
        )
        (progn
          (setq atts (cdr (assoc 10 (entget x))))
          ; store the first and second index of atts
          (setq y_coor (nth 1 atts))
          (setq lst2 (cons y_coor lst2))
          (setq x_coor (nth 0 atts))
          (setq lst2 (cons x_coor lst2))
          (princ (strcat "x_coor: " (rtos x_coor 2 2) " y_coor: " (rtos y_coor 2 2) "\n"))
          (setq lst1 (cons lst2 lst1))
          (setq lst2 '())
        )
      )
    )
    (setq target_layer_name (cdr target_layer_name))  ; 將這一行移至 while 循環中正確的位置
  )
  (setq lst1 lst1)
)

;------------------------------------------MAIN CODE TO BE RUNNING------------------------------------------
(vl-load-com)
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
    (setq target_layer (preloop_for_plan_eval_drawing dirpath dwgname_list))
    (mainloop_for_Dia_plan_eval dirpath target_file target_layer)
    (setq target_layer (preloop dirpath dwgname_list))
    (setq target_layer_0 (nth 0 target_layer))
    (setq target_layer_1 (nth 1 target_layer))
    (setq target_file (vl-remove-if ''( (item) (not (or (member item target_layer_0) (member item target_layer_1)))) target_file))
    (mainloop1 dirpath target_file target_layer)
    (startapp "dist\\Data Process - Plan Drawings.exe" dirpath)
  ))
; (if (and (= dtype "Elevation Drawings") (= wtype "Diaphragm"))
;   (progn
;     (setq dirpath (acet-ui-pickdir (strcat "Select the DIAPHRAGM WALL " (vl-princ-to-string dtype) " folder: ") 
;                 (getvar "dwgprefix")
;               )) ;or write (getvar "dwgprefix")
;     (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1))
;     (setq target_file (vl-directory-files dirpath "*.dwg" 1))
;     (setq *layoutname_list* '())
;     (setq target_layer (preloop dirpath dwgname_list))
;     (setq target_layer_0 (nth 0 target_layer))
;     (setq target_layer_1 (nth 1 target_layer))
;     (setq target_file (vl-remove-if ''( (item) (not (or (member item target_layer_0) (member item target_layer_1)))) target_file))
;     (mainloop2 dirpath target_file target_layer)
;     (startapp "dist\\Data Process - Elevation Drawings.exe" dirpath)
;   ))
(if (and (= dtype "Elevation Drawings") (= wtype "Diaphragm"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the DIAPHRAGM WALL " (vl-princ-to-string dtype) " folder: ") 
                (getvar "dwgprefix")
              )) ;or write (getvar "dwgprefix")
    (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1))
    (setq target_file (vl-directory-files dirpath "*.dwg" 1))
    (setq *layoutname_list* '())
    (setq target_layer (preloop_for_plan_eval_drawing dirpath dwgname_list))
    (mainloop_for_Dia_plan_eval dirpath target_file target_layer)
    (setq command (strcat "dist\\main.exe -t Diaphragm -d eval -c " dirpath "\\LineInfo.csv"))
    (startapp command)
  ))
; if dynamic type is Structural Descriptions and wtype is Diaphragm
; (if (and (= dtype "Structural Descriptions")(= wtype "Diaphragm"))
;   (progn
;     (command "BACKGROUNDPLOT" 2)
;     (setq *temp* (getfiled (strcat "Select the DIAPHRAGM WALL " (vl-princ-to-string dtype) " folder") "" "dwg" 8))
;     (setq filepath *temp*)
;     (setq filepath2 *temp*)
;     (setq dirpath (substr *temp* 1 (vl-string-position (ascii "\\") *temp* nil t)))
;     (setq filename (list (vl-string-left-trim dirpath *temp*)))
;     (setq *layoutname_list* '())
;     (mainloop3 filepath dirpath filename)
;     (setq command (strcat "dist\\main.exe -t Diaphragm -d structure -c " dirpath "\\FullText.csv"))
;     (startapp command)
;   ))
(if (and (= dtype "Structural Descriptions")(= wtype "Diaphragm"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the Diaphragm " (vl-princ-to-string dtype) " folder: ") 
                (getvar "dwgprefix")
              ))
    (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1)) 
    (setq target_file (vl-directory-files dirpath "*.dwg" 1))
    (setq *layoutname_list* '())
    (mainloop3 dirpath dwgname_list)
    (setq command (strcat "dist\\main.exe -t Diaphragm -d structure -c " dirpath "\\FullText.csv"))
    (startapp command)
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
    (setq command (strcat "dist\\main.exe -t Diaphragm -d rebar -c " dirpath "\\FullText.csv -c2 " dirpath "\\vertical_line.csv -c3 " dirpath "\\helper_line.csv -c4 " dirpath "\\Sh_helper.csv"))
    ;(startapp "dist\\Data Process - Rebar Drawings.exe" dirpath)
    (startapp command)
  ))

; ------------------------------------------------For Sheet Pile ------------------------------------------------------
; 鋼板樁平面圖
(if (and (= dtype "Plan Drawings") (= wtype "SheetPile"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the Sheet Pile WALL " (vl-princ-to-string dtype) " folder: ") 
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
    (setq command (strcat "dist\\main.exe -t SheetPile -d eval -c " dirpath "\\FullText.csv"))
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
    (setq command (strcat "dist\\main.exe -t SheetPile -d rebar -c " dirpath "\\FullText.csv"))
    (startapp command)
  )
)

; ------------------------------------------------For BoredPile ------------------------------------------------------
(if (and (= dtype "Plan Drawings") (= wtype "BoredPile"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the Bored Pile " (vl-princ-to-string dtype) " folder: ") 
                (getvar "dwgprefix")
              )) ;or write (getvar "dwgprefix")
    (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1)) 
    (setq target_file (vl-directory-files dirpath "*.dwg" 1))
    (setq *layoutname_list* '())
    (setq target_layer (preloop_for_selectlayer_folder dirpath dwgname_list))
    (setq wall_file (nth 0 target_layer))
    (setq text_file (nth 1 target_layer))
    (setq wall_layer (nth 2 target_layer))
    (setq text_layer (nth 3 target_layer))
    (output_pile_info dirpath target_file target_layer)
    (publish_all_folder dirpath dwgname_list)
    (setq command (strcat "dist\\main.exe -t BoredPile -d plan -p " dirpath "\\-Layout1.pdf -c " dirpath "\\pile.csv"))
    (startapp command)
  )
)
(if (and (= dtype "Rebar Drawings") (= wtype "BoredPile"))
  (progn
    (setq dirpath (acet-ui-pickdir (strcat "Select the Bored Pile " (vl-princ-to-string dtype) " folder: ") 
                (getvar "dwgprefix")
              ))
    (setq dwgname_list (vl-directory-files dirpath "*.dwg" 1)) 
    (setq target_file (vl-directory-files dirpath "*.dwg" 1))
    (setq *layoutname_list* '())
    (preloopp_for_all_folder dirpath dwgname_list)
    (setq command (strcat "dist\\main.exe -t BoredPile -d rebar -c " dirpath "\\FullText.csv"))
    (startapp command)
  )
)
(if (and (= dtype "Structural Descriptions") (= wtype "BoredPile"))
  (progn
    (command "BACKGROUNDPLOT" 2)
    (setq *temp* (getfiled (strcat "Select the DIAPHRAGM WALL " (vl-princ-to-string dtype) " folder") "" "dwg" 8))
    (setq filepath *temp*)
    (setq filepath2 *temp*)
    (setq dirpath (substr *temp* 1 (vl-string-position (ascii "\\") *temp* nil t)))
    (setq filename (list (vl-string-left-trim dirpath *temp*)))
    (setq *layoutname_list* '())
    (mainloop3 filepath dirpath filename)
    (setq command (strcat "dist\\main.exe -t BoredPile -d structure -c " dirpath "\\FullText.csv"))
    (startapp command)
  )
)
(command "FILEDIA" OldFda)
(command "BACKGROUNDPLOT" OldBgp)
(command "LAYEREVALCTL" OldLayEva)
(princ "Extraction Complete")
(princ)
