# just some classes to help with management and concepts for teacher and student models

class modelScore():
    def __init__(self, scoreName: str, modelName: str):
        self.scoreName = scoreName
        self.modelName = modelName

class teacherStudentPair():
    def __init__(self, teacherScoreName: str, studentScoreName: str, teacherName:str, studentName:str):
        self.teacherModel = modelScore(teacherScoreName, teacherName)
        self.studentModel = modelScore(studentScoreName, studentName)

    @property
    def studentScoreDeltaName(self):
        return f"{self.studentModel.scoreName}_delta"
    @property
    def absStudentScoreDeltaName(self):
        return f"{self.studentScoreDeltaName}_abs"
    @property
    def adjustedTeacherScoreName(self):
        return f"{self.teacherModel.scoreName}_adjusted"

    @property
    def studentScoreDeltaDefinition(self):
        return f"{self.studentModel.scoreName} - {self.adjustedTeacherScoreName}"
    @property
    def absStudentScoreDeltaDefinition(self):
        return f"abs({self.studentScoreDeltaName})"

    def applyFrameDefinitions(self, frame):
        frame = frame.Define(
            self.studentScoreDeltaName,
            self.studentScoreDeltaDefinition,
        )
        frame = frame.Define(
            self.absStudentScoreDeltaName,
            self.absStudentScoreDeltaDefinition,
        )
        return frame

class teacherStudentGroup():
    def __init__(self, teacherScoreName: str, studentScoreNames: list, teacherName:str, studentNames: list):
        self.teacherModel = modelScore(teacherScoreName, teacherName)
        
        assert(len(studentScoreNames) == len(studentNames)), "Student score names and student names were mismatched sizes"
        self.studentModels = {}
        paramZip = list(zip(studentScoreNames, studentNames))
        for params in paramZip:
            self.studentModels[params[1]] = modelScore(*params)
            
        self.teacherStudentPairs = []
        for studentModelName in self.studentModels:
            self.teacherStudentPairs.append(
                teacherStudentPair(
                    self.teacherModel.scoreName,
                    self.studentModels[studentModelName].scoreName,
                    self.teacherModel.modelName,
                    self.studentModels[studentModelName].modelName,
                )
            )
    @property
    def adjustedTeacherScoreName(self):
        return f"{self.teacherModel.scoreName}_adjusted"

    @property
    def adjustedTeacherScoreDefinition(self):
        #return f"pow(2.0, {self.teacherModel.scoreName})"
        return f"log({self.teacherModel.scoreName}) * 32"

    def applyFrameDefinitions(self, frame):
        frame = frame.Define(
            self.adjustedTeacherScoreName,
            self.adjustedTeacherScoreDefinition
        )

        for theTeacherStudentPair in self.teacherStudentPairs:
            frame = theTeacherStudentPair.applyFrameDefinitions(frame)
        return frame
        
class HTModel(modelScore):
    def __init__(self, scoreName: str, modelName: str):
        super().__init__(scoreName, modelName)
    
    @property
    def HTDefinition(self):
        return """
        try {
        for(int i = 0; i < L1Upgrade.sumType.size(); ++i){
           if(L1Upgrade.sumType.at(i) == 1 and L1Upgrade.sumBx.at(i) == 0){
              return (double) L1Upgrade.sumEt.at(i);
           }
        }
        return 0.0;
        }
        catch (const std::runtime_error& e) {
           return 0.0;
        }
        """

    def applyFrameDefinitions(self, frame):
        frame = frame.Define(
            self.scoreName,
            self.HTDefinition
        )
        return frame

class CICADAInputModelScore(modelScore):
    def __init__(self, scoreName: str, modelName: str):
        super().__init__(scoreName, modelName)
    
    @property
    def CICADAInputScoreDefinition(self):
        return """
        int sum = 0;
        try {
           for(int i = 0; i < 18; ++i) {
              for(int j = 0; j < 14; ++j){
                 sum += modelInput[i*14+j];
              }
           }
           return sum;
        }
        catch (const std::runtime_error& e) {
           return 0;
        }
        """

    def applyFrameDefinitions(self, frame):
        frame = frame.Define(
            self.scoreName,
            self.CICADAInputScoreDefinition
        )
        return frame

CICADA_vXp2p0_Group = teacherStudentGroup(
            'CICADA_vXp2p0_teacher_score',
            ['CICADA_v1p2p0_score', 'CICADA_v2p2p0_score'],
            'vXp2p0',
            ['v1p2p0', 'v2p2p0'],
)

CICADA_vXp2p0N_Group = teacherStudentGroup(
            'CICADA_vXp2p0N_teacher_score',
            ['CICADA_v1p2p0N_score', 'CICADA_v2p2p0N_score'],
            'vXp2p0N',
            ['v1p2p0N', 'v2p2p0N'],
)
CICADA_vXp2p1_Group = teacherStudentGroup(
            'CICADA_vXp2p1_teacher_score',
            ['CICADA_v1p2p1_score', 'CICADA_v2p2p1_score'],
            'vXp2p1',
            ['v1p2p1', 'v2p2p1'],
)

CICADA_vXp2p1N_Group = teacherStudentGroup(
            'CICADA_vXp2p1N_teacher_score',
            ['CICADA_v1p2p1N_score', 'CICADA_v2p2p1N_score'],
            'vXp2p1N',
            ['v1p2p1N', 'v2p2p1N'],
)

toyHTModel = HTModel("HT", "HTModel")

CICADAInputScore = CICADAInputModelScore("CICADAInputSum", "CICADAInputSum")
