within ;

model unicode "Model with a variable that has a Unicode description"

  Real DeltaTheta=sin(time) "ΔΘ";
equation

  annotation (experiment(StopTime=20));
end unicode;
