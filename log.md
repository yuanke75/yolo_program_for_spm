3.24    23:32  训练020,030两类分子，使用大数据集，epoch为10  Logging results to runs\train\exp30
        2:30 完成训练
        结果为
        Validating runs\train\exp30\weights\best.pt...
        Fusing layers... 
        gelan-e summary: 690 layers, 57286553 parameters, 50867081 gradients, 188.6 GFLOPs
                        Class     Images  Instances          P          R      mAP50   mAP50-95: 100%|██████████| 1124/1124 01:13
                        all       1124       7462          1          1      0.995      0.984
                            20       1124       4872          1          1      0.995      0.978
                            30       1124       2590          1          1      0.995       0.99

![alt text](runs/detect/exp19/0212_LMM_022_15nm.jpg)
            以上是训练020和030的预测结果
        
        
        以下作废

        <!-- 进行024小数据集的30个epoch训练，想确定能不能达到95以上的map，直接用的用的train.py，Logging results to runs\train\exp31
        相当于是只使用 “回放” 作为增量学习的手段，而并没有采取其他策略
        Validating runs\train\exp31\weights\best.pt...
        Fusing layers...
        gelan-e summary: 690 layers, 57286553 parameters, 50867081 gradients, 188.6 GFLOPs
                        Class     Images  Instances          P          R      mAP50   mAP50-95: 100%|██████████| 8/8 00:01
                        all         46        506      0.953      0.983      0.994      0.885
                            20         46        161      0.898          1      0.994      0.895
                            30         46        115          1      0.959      0.995      0.874
                            24         46        230      0.962      0.991      0.993      0.885
        [    0.94602     0.97893     0.97653]
![alt text](runs/detect/exp20/zirec.jpg)
            从预测和训练结果说明024的训练集需要改善 -->
        
        以上作废


        改善数据集，新选一张图标签了17个024分子，数据集包含621张图片
        使用新的数据集来训练024，改成15个epoch，目的是得到证明可以最后模型在验证集上的指标在90或95以上
        Validating runs\train\exp32\weights\best.pt...
        Fusing layers... 
        gelan-e summary: 690 layers, 57286553 parameters, 50867081 gradients, 188.6 GFLOPs
                        Class     Images  Instances          P          R      mAP50   mAP50-95: 100%|██████████| 10/10 00:02
                        all         56        763      0.977      0.993      0.994       0.83
                        24         56        763      0.977      0.993      0.994       0.83
        如果epoch达到20，可能效果更好
![alt text](runs/detect/exp21/zirec.jpg)
![alt text](runs/detect/exp22/zirec.jpg)
        为训练后验证的图片


        需要进行贝叶斯优化，第一步在验证集中加入020和030
        第一次测试直接运行trainadd，epoch修改为20，命令行中的初始权重文件使用D:/code/yolov9-main/fisher/ewc_model_task_train.pt，失败
        第二次测试，命令行中的初始权重文件使用runs/train/exp30/weights/best.pt，数据区域正常，需要调参，超参数文件为
[text](temp_hyp/list4/hyp_trial_7.yaml)
        Validating runs\train\exp35\weights\best.pt...
        Fusing layers... 
        gelan-e summary: 690 layers, 57286553 parameters, 50867081 gradients, 188.6 GFLOPs
                        Class     Images  Instances          P          R      mAP50   mAP50-95: 100%|██████████| 16/16 00:04
                        all         96       1138      0.836      0.932      0.896       0.79
                            20         96        231          1      0.817      0.963      0.915
                            30         96        144      0.918          1      0.995      0.949
                            24         96        763      0.589       0.98      0.729      0.506
        [    0.89906     0.95739     0.73625]
        Results saved to runs\train\exp35
![alt text](runs/detect/exp24/0212_LMM_022_15nm.jpg)问题在于虽然数据显示还行，但是预测的图片老任务的类别很多被识别成了新任务的类别

        验证集要包含老任务的所有验证集

        修改超参数文件再测试一次
        使用detect.py生成txt文件放入验证集中

        Validating runs\train\exp39\weights\best.pt...
        Fusing layers... 
        gelan-e summary: 690 layers, 57286553 parameters, 50867081 gradients, 188.6 GFLOPs
                        Class     Images  Instances          P          R      mAP50   mAP50-95: 100%|██████████| 1/1 00:00
                        all          1         64      0.952      0.974      0.992      0.952
                        20          1         35      0.938      0.971      0.989      0.956
                        30          1         29      0.966      0.977      0.994      0.947
        [    0.95424     0.97158]
        Results saved to runs\train\exp39  这个为以后用于老模型的权重