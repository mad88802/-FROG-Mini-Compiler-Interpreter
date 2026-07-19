FRG_Begin
## exemple: déclaration et boucle Repeat
FRG_Int i, x1 #
FRG_Real x3 #
FRG_Strg msg #
i:=30 #
If [ i<=20 ]
Begin
   x1:=10 #
End
Else
Begin
   x1:=30 #
   x3:=x1*4 #
   FRG_Print x1, x3 #
End
FRG_Print " Hello :) " #
Repeat
   i:=i-5 #
   FRG_Print i #
until [ i <= 15 ]
FRG_End
