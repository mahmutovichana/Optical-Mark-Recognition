import cv2
import numpy as np
import utils
from tkinter import Tk, Frame, Button, Label, messagebox, filedialog, Radiobutton
import keyboard


class AutoGraderApp:
    def __init__(self):
        self.webCamFeed = False
        self.pathImage = ""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(10, 160)
        self.heightImg = 700
        self.widthImg = 700
        self.questions = 5
        self.choices = 5
        self.ans = [1, 2, 0, 2, 4]
        self.count = 0

        self.root = Tk()
        self.root.title("AutoGrader")
        self.root.geometry("600x720")
        self.root.configure(bg="lightblue")

        self.intro_frame = Frame(self.root, bg="lightblue")
        self.intro_frame.pack(side="top", padx=20, pady=20)

        self.text_label = Label(self.intro_frame, text="Dobrodošli u AutoGrader!", font=("Arial", 20), bg="lightblue")
        self.text_label.pack(pady=20)

        self.description_label = Label(self.intro_frame,
                                       text="AutoGrader je aplikacija za automatsko ocjenjivanje odgovora na testovima. "
                                            "Možete koristiti kameru ili učitati sliku sa testom.",
                                       font=("Arial", 14), bg="lightblue", wraplength=400, justify="center")
        self.description_label.pack(pady=10)

        self.select_label = Label(self.intro_frame, text="Odaberite opciju:", font=("Arial", 16), bg="lightblue")
        self.select_label.pack()

        self.camera_button = Button(self.intro_frame, text="Koristi kameru", command=self.use_camera,
                                    font=("Arial", 14), bg="lightgreen", fg="black")
        self.camera_button.pack(pady=10)

        self.photo_button = Button(self.intro_frame, text="Učitaj sliku", command=self.upload_photo, font=("Arial", 14),
                                   bg="lightgreen", fg="black")
        self.photo_button.pack(pady=0)

        # Hover efekti za dugmad
        self.camera_button.bind("<Enter>", lambda event: self.camera_button.config(bg="lightgreen", fg="white"))
        self.camera_button.bind("<Leave>", lambda event: self.camera_button.config(bg="lightgreen", fg="black"))

        self.photo_button.bind("<Enter>", lambda event: self.photo_button.config(bg="lightgreen", fg="white"))
        self.photo_button.bind("<Leave>", lambda event: self.photo_button.config(bg="lightgreen", fg="black"))

        self.questions_frame = Frame(self.root, bg="lightblue")
        self.questions_frame.pack(side="top", padx=20, pady=20)

        self.header_label = Label(self.questions_frame, text="Odredite tačne odgovore:", font=("Arial", 12),
                                  bg="lightblue")
        self.header_label.pack(pady=10)

        self.options = []
        for i in range(self.questions):
            question_label = Label(self.questions_frame, text=f"Pitanje {i + 1}:", font=("Arial", 12), bg="lightblue")
            question_label.pack(pady=0)

            question_options = []
            option_frame = Frame(self.questions_frame, bg="lightblue")
            option_frame.pack(anchor="center")

            for j in range(self.choices):
                option_button = Radiobutton(option_frame, text=f"Odgovor {j + 1}", font=("Arial", 10),
                                            command=lambda p=i, q=j: self.mark_answer(p, q))
                option_button.pack(side="left")
                question_options.append(option_button)

            self.options.append(question_options)

        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()

    def mark_answer(self, question_idx, answer_idx):
        # Clear the selection for the question
        for option_button in self.options[question_idx]:
            option_button.config(bg="lightgrey", fg="black")

        # Mark the selected answer
        self.options[question_idx][answer_idx].config(bg="lightgreen", fg="white")

        # Update the correct answer for the question in the class attribute
        self.ans[question_idx] = answer_idx

    def use_camera(self):
        self.webCamFeed = True
        self.start_auto_grader()

    def upload_photo(self):
        self.webCamFeed = False
        self.pathImage = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if self.pathImage:
            self.start_auto_grader()

    def start_auto_grader(self):
        if self.webCamFeed:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(10, 160)

        while True:
            if self.webCamFeed:
                success, img = self.cap.read()
            else:
                img = cv2.imread(self.pathImage)

            if img is None:
                messagebox.showerror("Greška", "Nemoguće učitati sliku.")
                self.cap.release()
                cv2.destroyAllWindows()
                return

            img = cv2.resize(img, (self.widthImg, self.heightImg))  # RESIZE IMAGE
            imgFinal = img.copy()
            imgBlank = np.zeros((self.heightImg, self.widthImg, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGGING IF REQUIRED
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
            imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # ADD GAUSSIAN BLUR
            imgCanny = cv2.Canny(imgBlur, 10, 70)  # APPLY CANNY

            try:
                # FIND ALL CONTOURS
                imgContours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
                imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
                contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # FIND ALL CONTOURS
                cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS
                rectCon = utlis.rectContour(contours)  # FILTER FOR RECTANGLE CONTOURS
                biggestPoints = utlis.getCornerPoints(rectCon[0])  # GET CORNER POINTS OF THE BIGGEST RECTANGLE
                gradePoints = utlis.getCornerPoints(rectCon[1])  # GET CORNER POINTS OF THE SECOND-BIGGEST RECTANGLE

                if biggestPoints.size != 0 and gradePoints.size != 0:

                    # BIGGEST RECTANGLE WARPING
                    biggestPoints = utlis.reorder(biggestPoints)  # REORDER FOR WARPING
                    cv2.drawContours(imgBigContour, biggestPoints, -1, (0, 255, 0), 20)  # DRAW THE BIGGEST CONTOUR
                    pts1 = np.float32(biggestPoints)  # PREPARE POINTS FOR WARP
                    pts2 = np.float32([[0, 0], [self.widthImg, 0], [0, self.heightImg], [self.widthImg, self.heightImg]])  # PREPARE POINTS FOR WARP
                    matrix = cv2.getPerspectiveTransform(pts1, pts2)  # GET TRANSFORMATION MATRIX
                    imgWarpColored = cv2.warpPerspective(img, matrix, (self.widthImg, self.heightImg))  # APPLY WARP PERSPECTIVE

                    # SECOND BIGGEST RECTANGLE WARPING
                    cv2.drawContours(imgBigContour, gradePoints, -1, (255, 0, 0), 20)  # DRAW THE BIGGEST CONTOUR
                    gradePoints = utlis.reorder(gradePoints)  # REORDER FOR WARPING
                    ptsG1 = np.float32(gradePoints)  # PREPARE POINTS FOR WARP
                    ptsG2 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])  # PREPARE POINTS FOR WARP
                    matrixG = cv2.getPerspectiveTransform(ptsG1, ptsG2)  # GET TRANSFORMATION MATRIX
                    imgGradeDisplay = cv2.warpPerspective(img, matrixG, (325, 150))  # APPLY WARP PERSPECTIVE

                    # APPLY THRESHOLD
                    imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)  # CONVERT TO GRAYSCALE
                    imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]  # APPLY THRESHOLD AND INVERSE

                    boxes = utlis.splitBoxes(imgThresh)  # GET INDIVIDUAL BOXES
                    cv2.imshow("Split Test ", boxes[3])
                    countR = 0
                    countC = 0
                    myPixelVal = np.zeros((self.questions, self.choices))  # TO STORE THE NON ZERO VALUES OF EACH BOX
                    for image in boxes:
                        # cv2.imshow(str(countR)+str(countC),image)
                        totalPixels = cv2.countNonZero(image)
                        myPixelVal[countR][countC] = totalPixels
                        countC += 1
                        if countC == self.choices:
                            countC = 0
                            countR += 1

                    # FIND THE USER ANSWERS AND PUT THEM IN A LIST
                    myIndex = []
                    for x in range(0, self.questions):
                        arr = myPixelVal[x]
                        myIndexVal = np.where(arr == np.amax(arr))
                        myIndex.append(myIndexVal[0][0])
                    # print("USER ANSWERS",myIndex)

                    # COMPARE THE VALUES TO FIND THE CORRECT ANSWERS
                    grading = []
                    for x in range(0, self.questions):
                        if self.ans[x] == myIndex[x]:
                            grading.append(1)
                        else:
                            grading.append(0)
                    # print("GRADING",grading)
                    score = (sum(grading) / self.questions) * 100  # FINAL GRADE
                    # print("SCORE",score)

                    # DISPLAYING ANSWERS
                    utlis.showAnswers(imgWarpColored, myIndex, grading, self.ans)  # DRAW DETECTED ANSWERS
                    utlis.drawGrid(imgWarpColored)  # DRAW GRID
                    imgRawDrawings = np.zeros_like(imgWarpColored)  # NEW BLANK IMAGE WITH WARP IMAGE SIZE
                    utlis.showAnswers(imgRawDrawings, myIndex, grading, self.ans)  # DRAW ON NEW IMAGE
                    invMatrix = cv2.getPerspectiveTransform(pts2, pts1)  # INVERSE TRANSFORMATION MATRIX
                    imgInvWarp = cv2.warpPerspective(imgRawDrawings, invMatrix, (self.widthImg, self.heightImg))  # INV IMAGE WARP

                    # DISPLAY GRADE
                    imgRawGrade = np.zeros_like(imgGradeDisplay, np.uint8)  # NEW BLANK IMAGE WITH GRADE AREA SIZE
                    cv2.putText(imgRawGrade, str(int(score)) + "%", (70, 100), cv2.FONT_HERSHEY_COMPLEX, 3, (0, 255, 255), 3)  # ADD THE GRADE TO NEW IMAGE
                    invMatrixG = cv2.getPerspectiveTransform(ptsG2, ptsG1)  # INVERSE TRANSFORMATION MATRIX
                    imgInvGradeDisplay = cv2.warpPerspective(imgRawGrade, invMatrixG, (self.widthImg, self.heightImg))  # INV IMAGE WARP

                    # SHOW ANSWERS AND GRADE ON FINAL IMAGE
                    imgFinal = cv2.addWeighted(imgFinal, 1, imgInvWarp, 1, 0)
                    imgFinal = cv2.addWeighted(imgFinal, 1, imgInvGradeDisplay, 1, 0)

                    # IMAGE ARRAY FOR DISPLAY
                    imageArray = ([img, imgGray, imgCanny, imgContours],
                                  [imgBigContour, imgThresh, imgWarpColored, imgFinal])
                    cv2.imshow("Final Result", imgFinal)
            except:
                imageArray = ([img, imgGray, imgCanny, imgContours],
                              [imgBlank, imgBlank, imgBlank, imgBlank])

            # LABELS FOR DISPLAY
            labels = [["Original", "Gray", "Edges", "Contours"],
                      ["Biggest Contour", "Threshold", "Warped", "Final"]]

            stackedImage = utlis.stackImages(imageArray, 0.5, labels)
            cv2.imshow("Result", stackedImage)

            # SAVE IMAGE WHEN 's' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('s'):
                cv2.imwrite("Scanned/myImage" + str(self.count) + ".jpg", imgFinal)
                cv2.rectangle(stackedImage, (0, 200), (640, 300), (0, 255, 0), cv2.FILLED)
                cv2.putText(stackedImage, "Scan Saved", (150, 265), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 2)
                cv2.imshow("Result", stackedImage)
                cv2.waitKey(300)
                self.count += 1

            # SHOW THE FINAL RESULT
            cv2.imshow("Result", stackedImage)

            if keyboard.is_pressed('q'):  # CHECK IF 'q' IS PRESSED
                break  # CLOSE ALL WINDOWS FOR THE PROCESSED VIDEO/PHOTO

        # RELEASE THE CAPTURE AND DESTROY ALL WINDOWS
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = AutoGraderApp()
