class DocumentClassifier:
    def classify(self, raw_text):
        # סימנים ייחודיים לסוג A (נמצאים בטבלאות של a_r_9 ו-a_r_25)
        a_indicators = ["הפסקה", "% 125", "% 150", "100%", "מקום"]
        
        # סימנים ייחודיים לסוג N (נמצאים בכותרות של n_r_10 ו-n_r_5)
        n_indicators = ["מחיר לשעה", "סה\"כ לתשלום", "כרטיס עובד לחודש"]
        
        a_score = sum(1 for word in a_indicators if word in raw_text)
        n_score = sum(1 for word in n_indicators if word in raw_text)
        
        if a_score > n_score:
            return "A"
        return "N"