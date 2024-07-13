; -------------- GUI Function to get the target retaining wall type --------
(defun wtype_selection ( / wtype)
  (setq option '("Diaphragm" "SheetPile" "BoredPile"))
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

; -------------- GUI Function to get the target drawing type ---------------
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

; -------------- Function to make dsd for publish the file --------------
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

;---------------- Function to export data to CSV ------------------------
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

; ---------------- Function to turn on all layers ------------------------
(defun turnon_alllayer (doc / layertable layer)
  (setq layertable (vla-get-layers doc))
  (vlax-for layer layertable
      (vla-put-LayerOn layer :vlax-true)  ; 設置圖層為可打印
      (vla-put-plottable layer :vlax-true)
  )
)

; ---------------- Function to filter the target layer -------------------
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

; ---------------- Function to publish all the file in the folder ---------
(defun publish_all_folder(dirpath dwgname_list)
  (makedsd dirpath dwgname_list "-Layout1.pdf" "PUBLIST.dsd")
  (command "-Publish" (strcat dirpath "\\" "PUBLIST.dsd") )
)

; ---------------- Function to publish the file by layer -------------------
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

; ---------------- Some basic functions ---------------------------------
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