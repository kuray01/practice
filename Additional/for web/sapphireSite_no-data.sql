USE SapphireSite
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE FUNCTION [dbo].[GetAverageWeight] (@UserId INT, @StartDate DATE, @EndDate DATE)
RETURNS DECIMAL(5, 2)
AS
BEGIN
    DECLARE @AvgWeight DECIMAL(5, 2);
    SELECT @AvgWeight = AVG(weight)
    FROM WeightStats
    WHERE user_id = @UserId AND weigh_date BETWEEN @StartDate AND @EndDate;
    RETURN ISNULL(@AvgWeight, 0.0);
END
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE FUNCTION [dbo].[GetCategoryByCalories] (@Calories INT)
RETURNS NVARCHAR(20)
AS
BEGIN
    DECLARE @Category NVARCHAR(20);
    SELECT @Category =
        CASE
            WHEN @Calories < 300 THEN N'Легкий перекус'
            WHEN @Calories BETWEEN 300 AND 600 THEN N'Основное блюдо'
            ELSE N'Высококалорийное'
        END;
    RETURN @Category;
END
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE FUNCTION [dbo].[GetTotalCaloriesByDate] (@UserId INT, @MealDate DATE)
RETURNS INT
AS
BEGIN
    DECLARE @TotalCalories INT;
    SELECT @TotalCalories = SUM(calories)
    FROM Meals
    WHERE user_id = @UserId AND meal_date = @MealDate;
    RETURN ISNULL(@TotalCalories, 0);
END
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE FUNCTION [dbo].[IsWeightNormal] (@Weight DECIMAL(5, 2), @Height INT)
RETURNS BIT
AS
BEGIN
    DECLARE @BMI DECIMAL(5, 2);
    SET @BMI = (@Weight / POWER(CAST(@Height AS DECIMAL(5, 2)) / 100, 2));
    RETURN IIF(@BMI >= 18.5 AND @BMI <= 24.9, 1, 0);
END
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[__EFMigrationsHistory](
	[MigrationId] [nvarchar](150) NOT NULL,
	[ProductVersion] [nvarchar](32) NOT NULL,
 CONSTRAINT [PK___EFMigrationsHistory] PRIMARY KEY CLUSTERED
(
	[MigrationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Articles](
	[ArticleId] [int] IDENTITY(1,1) NOT NULL,
	[Title] [nvarchar](100) NULL,
	[Content] [nvarchar](max) NULL,
	[Category] [nvarchar](50) NULL,
PRIMARY KEY CLUSTERED
(
	[ArticleId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DailyIntake](
	[IntakeId] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [int] NULL,
	[Date] [date] NULL,
	[Calories] [int] NULL,
	[Protein] [float] NULL,
	[Fat] [float] NULL,
	[Carbs] [float] NULL,
PRIMARY KEY CLUSTERED
(
	[IntakeId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Meals](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[user_id] [int] NOT NULL,
	[name] [nvarchar](100) NOT NULL,
	[category] [nvarchar](20) NOT NULL,
	[calories] [int] NOT NULL,
	[meal_date] [date] NULL,
PRIMARY KEY CLUSTERED
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Recipes](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[user_id] [int] NOT NULL,
	[title] [nvarchar](100) NOT NULL,
	[ingredients] [nvarchar](max) NOT NULL,
	[instructions] [nvarchar](max) NOT NULL,
	[created_at] [datetime] NULL,
PRIMARY KEY CLUSTERED
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Users](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[email] [nvarchar](255) NOT NULL,
	[password_hash] [nvarchar](255) NOT NULL,
	[name] [nvarchar](25) NOT NULL,
	[birth_date] [date] NOT NULL,
	[weight] [decimal](5, 2) NOT NULL,
	[height] [int] NOT NULL,
	[created_at] [datetime] NULL,
	[Lifestyle] [varchar](20) NULL,
	[Goal] [varchar](20) NULL,
	[DailyCalorieTarget] [int] NULL,
	[IMT] [decimal](5, 2) NULL,
PRIMARY KEY CLUSTERED
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WeightStats](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[user_id] [int] NOT NULL,
	[weight] [decimal](5, 2) NOT NULL,
	[weigh_date] [date] NOT NULL,
	[Date] [datetime] NULL,
PRIMARY KEY CLUSTERED
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET IDENTITY_INSERT [dbo].[Meals] ON

SET IDENTITY_INSERT [dbo].[WeightStats] OFF
GO
SET ANSI_PADDING ON
GO

ALTER TABLE [dbo].[Users] ADD UNIQUE NONCLUSTERED
(
	[email] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

ALTER TABLE [dbo].[WeightStats] ADD  CONSTRAINT [uq_user_weigh_date] UNIQUE NONCLUSTERED
(
	[user_id] ASC,
	[weigh_date] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Articles] ADD  DEFAULT (N'Психология') FOR [Category]
GO
ALTER TABLE [dbo].[DailyIntake] ADD  DEFAULT (getdate()) FOR [Date]
GO
ALTER TABLE [dbo].[DailyIntake] ADD  DEFAULT ((0)) FOR [Calories]
GO
ALTER TABLE [dbo].[DailyIntake] ADD  DEFAULT ((0)) FOR [Protein]
GO
ALTER TABLE [dbo].[DailyIntake] ADD  DEFAULT ((0)) FOR [Fat]
GO
ALTER TABLE [dbo].[DailyIntake] ADD  DEFAULT ((0)) FOR [Carbs]
GO
ALTER TABLE [dbo].[Meals] ADD  DEFAULT (CONVERT([date],getdate())) FOR [meal_date]
GO
ALTER TABLE [dbo].[Recipes] ADD  DEFAULT (getdate()) FOR [created_at]
GO
ALTER TABLE [dbo].[Users] ADD  DEFAULT (getdate()) FOR [created_at]
GO
ALTER TABLE [dbo].[DailyIntake]  WITH CHECK ADD FOREIGN KEY([UserId])
REFERENCES [dbo].[Users] ([id])
GO
ALTER TABLE [dbo].[Meals]  WITH CHECK ADD FOREIGN KEY([user_id])
REFERENCES [dbo].[Users] ([id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Recipes]  WITH CHECK ADD FOREIGN KEY([user_id])
REFERENCES [dbo].[Users] ([id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[WeightStats]  WITH CHECK ADD FOREIGN KEY([user_id])
REFERENCES [dbo].[Users] ([id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Meals]  WITH CHECK ADD CHECK  (([calories]>(0)))
GO
ALTER TABLE [dbo].[Meals]  WITH CHECK ADD CHECK  (([category]= N'Перекус' OR [category]= N'Ужин' OR [category]=
                                                                                                    N'Обед' OR [category]=
                                                                                                               N'Завтрак'))
GO
ALTER TABLE [dbo].[Users]  WITH CHECK ADD CHECK  (([height]>=(120) AND [height]<=(220)))
GO
ALTER TABLE [dbo].[Users]  WITH CHECK ADD CHECK  (([weight]>=(12) AND [weight]<=(90)))
GO
ALTER TABLE [dbo].[WeightStats]  WITH CHECK ADD CHECK  (([weight]>=(12) AND [weight]<=(150)))
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[AddMeal]
    @UserID INT,
    @Name NVARCHAR(100),
    @Category NVARCHAR(20),
    @Calories INT,
    @MealDate DATE
AS
BEGIN
    INSERT INTO Meals (user_id, name, category, calories, meal_date)
    VALUES (@UserID, @Name, @Category, @Calories, @MealDate);
END;
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[CheckUserWeight]
    @UserID INT
AS
BEGIN
    IF EXISTS (SELECT 1 FROM Users WHERE id = @UserID AND weight > 60)
    BEGIN
        PRINT N'Вес пользователя выше 60';
    END
    ELSE
    BEGIN
        PRINT N'Вес пользователя 60 или ниже';
    END
END;
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[GetAverageWeightForUser]
    @UserID INT,
    @AverageWeight DECIMAL(5, 2) OUTPUT
AS
BEGIN
    SELECT @AverageWeight = AVG(weight)
    FROM WeightStats
    WHERE user_id = @UserID;
END;
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[GetRecentUsers]
AS
BEGIN
    SELECT name, email, created_at
    FROM Users
    WHERE created_at >= DATEADD(DAY, -90, GETDATE());
END;
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[GetUserCount]
    @UserCount INT OUTPUT
AS
BEGIN
    SELECT @UserCount = COUNT(*)
    FROM Users;
END;
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[UpdateUserWeight]
    @UserID INT,
    @NewWeight DECIMAL(5, 2)
AS
BEGIN
    UPDATE Users
    SET weight = @NewWeight
    WHERE id = @UserID;
END;
GO